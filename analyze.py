#!/usr/bin/env python3
"""
v1.12 — automated rule-proposer for the LLM-critic loop.

Runs the current strategy, joins each trade with the entry-time feature panel,
and finds slices where outcomes differ materially from the overall distribution.
Emits a ranked list of candidate adaptive rules in the v1.11 hook syntax.

The output is the *input* to the critic loop: hypotheses to be sweep-validated.
Statistical caveats are surfaced explicitly (sample size, effect size, simple
significance) so candidates with small-n cells can be flagged for caution.

Usage:
    just analyze                          # report on TSLA and TSLL trade logs
    just analyze --tickers TSLA           # one ticker
    just analyze --features iv_rank,ret_14d,ema_stack,gamma_dollar   # focused subset
    just analyze --top 10                 # how many candidates to surface
"""

from __future__ import annotations
import argparse
import math
import sys
from dataclasses import asdict
import numpy as np
import pandas as pd

from scipy.stats import t as student_t

from data import build
from backtest import Backtester, compute_metrics, trades_to_dataframe
from strategies import get_config, pick_entry, check_exits, pick_roll
import pricing


# Default features to scan. Each is either:
#   - a `row` column from data.add_features (e.g. 'iv_rank', 'ret_14d')
#   - a peek-greek key, computed at entry time (prefix 'peek_'): peek_theta_yield, peek_gamma_dollar
# The peek values require the entry-time S/dte/delta/iv, joined via the trade record.
DEFAULT_FEATURES = [
    # already-bounded / ranged
    'iv_rank', 'iv_rank_3y', 'vix_rank', 'rsi_14',
    'ema_stack', 'bb_pctb',
    # returns
    'ret_1d', 'ret_5d', 'ret_14d', 'ret_30d',
    # vol context
    'iv_proxy', 'hv_30', 'vix',
    # volume
    'volume_surge',
    # intraday
    'intraday_return',
    # calendar
    'day_of_week', 'days_to_monthly_opex',
    'days_to_earnings', 'days_since_earnings',
    # peek-time greeks (computed below from entry-time params)
    'peek_theta_yield', 'peek_gamma_dollar', 'peek_credit_pct',
]


def _attach_features(trades_df: pd.DataFrame, feat_df: pd.DataFrame, cfg) -> pd.DataFrame:
    """Join entry-time features onto each trade. Also computes peek-greek
    metrics for the actual entered position so 'peek_*' features are available."""
    t = trades_df.copy()
    t['entry_date'] = pd.to_datetime(t['entry_date'])
    # Join `feat_df` by entry_date
    t = t.merge(feat_df, left_on='entry_date', right_index=True, how='left', suffixes=('', '_feat'))

    # Compute peek metrics for what was actually entered (use stored credit, iv_at_entry, dte_at_entry)
    peek_credit_pct = t['credit'] / t['strike']
    # theta_yield ≈ credit / dte_at_entry / credit = 1 / dte_at_entry  (poor — use BSM peek instead)
    # We re-peek from BSM with the entry-time params for a richer metric.
    peek_rows = []
    for _, r in t.iterrows():
        S_entry = float(r.get('close', float('nan')))
        if not np.isfinite(S_entry):
            peek_rows.append({'peek_theta_yield': np.nan, 'peek_gamma_dollar': np.nan})
            continue
        # delta sign — for puts the strike_from_delta uses positive target_delta
        # We can either rebuild the peek from S + dte + iv_at_entry + |delta|, OR just use stored credit + dte
        # Cleanest: BSM-peek with the *known* strike (skip strike_from_delta).
        iv = float(r['iv_at_entry']) if pd.notna(r['iv_at_entry']) else float('nan')
        dte = int(r['dte_at_entry']) if pd.notna(r['dte_at_entry']) else 0
        side = r['side']
        K = float(r['strike'])
        if not (iv > 0 and dte > 0 and K > 0 and side in ('put', 'call')):
            peek_rows.append({'peek_theta_yield': np.nan, 'peek_gamma_dollar': np.nan})
            continue
        T = dte / 365.0
        try:
            c = pricing.price(S_entry, K, T, iv, side, r=cfg.risk_free_rate)
            g = pricing.gamma(S_entry, K, T, iv, r=cfg.risk_free_rate)
            th = pricing.theta(S_entry, K, T, iv, side, r=cfg.risk_free_rate)
        except (ValueError, ZeroDivisionError):
            peek_rows.append({'peek_theta_yield': np.nan, 'peek_gamma_dollar': np.nan})
            continue
        theta_per_day = th / 365.0
        peek_rows.append({
            'peek_theta_yield': theta_per_day / c if c > 0 else np.nan,
            'peek_gamma_dollar': g * S_entry * S_entry * iv * iv / 365.0,
        })
    pk = pd.DataFrame(peek_rows, index=t.index)
    t = pd.concat([t, pk], axis=1)
    t['peek_credit_pct'] = peek_credit_pct.values
    return t


def _bucket_stats(group: pd.DataFrame, pnl_col: str = 'pnl_per_contract') -> dict:
    pnl = group[pnl_col].dropna()
    n = len(pnl)
    if n == 0:
        return {'n': 0, 'wr': float('nan'), 'avg': float('nan'), 'total': 0.0, 'std': float('nan')}
    return {
        'n': n,
        'wr': float((pnl > 0).mean() * 100),
        'avg': float(pnl.mean()),
        'total': float(pnl.sum()),
        'std': float(pnl.std(ddof=1)) if n > 1 else float('nan'),
    }


def _effect_size(buckets: dict, overall_mean: float) -> float:
    """Range of bucket means / overall std — simple 'how much do buckets spread'."""
    means = [b['avg'] for b in buckets.values() if b['n'] >= 5 and not math.isnan(b['avg'])]
    if len(means) < 2:
        return 0.0
    return max(means) - min(means)


def _t_stat(group_pnl: np.ndarray, rest_pnl: np.ndarray) -> float:
    """Welch t-stat for difference of means. Returns NaN if degenerate."""
    if len(group_pnl) < 3 or len(rest_pnl) < 3:
        return float('nan')
    m1, m2 = np.mean(group_pnl), np.mean(rest_pnl)
    v1, v2 = np.var(group_pnl, ddof=1), np.var(rest_pnl, ddof=1)
    n1, n2 = len(group_pnl), len(rest_pnl)
    se = math.sqrt(v1 / n1 + v2 / n2)
    if se == 0:
        return float('nan')
    return (m1 - m2) / se


def _t_pval(group_pnl: np.ndarray, rest_pnl: np.ndarray) -> tuple[float, float]:
    """Welch t-stat with two-sided p-value via Welch–Satterthwaite df."""
    if len(group_pnl) < 3 or len(rest_pnl) < 3:
        return float('nan'), float('nan')
    m1, m2 = np.mean(group_pnl), np.mean(rest_pnl)
    v1, v2 = np.var(group_pnl, ddof=1), np.var(rest_pnl, ddof=1)
    n1, n2 = len(group_pnl), len(rest_pnl)
    se2 = v1 / n1 + v2 / n2
    if se2 <= 0:
        return float('nan'), float('nan')
    t = (m1 - m2) / math.sqrt(se2)
    # Welch–Satterthwaite degrees of freedom
    df_num = se2 ** 2
    df_den = (v1 / n1) ** 2 / max(n1 - 1, 1) + (v2 / n2) ** 2 / max(n2 - 1, 1)
    df = df_num / df_den if df_den > 0 else max(n1 + n2 - 2, 1)
    pval = float(student_t.sf(abs(t), df) * 2.0)
    return float(t), pval


def _bh_correct(candidates: list[dict], alpha: float = 0.05) -> list[dict]:
    """Benjamini-Hochberg FDR correction. Sets 'passes_bh' on each candidate
    (sorted by p-value ascending). The largest k for which p_(k) ≤ k/m × α
    passes; all candidates with rank ≤ k are flagged True."""
    if not candidates:
        return []
    ranked = sorted(candidates, key=lambda c: c.get('pval', 1.0) if c.get('pval', 1.0) == c.get('pval', 1.0) else 1.0)
    m = len(ranked)
    pass_cutoff = -1
    for i, c in enumerate(ranked):
        p = c.get('pval', 1.0)
        if not (p == p):  # NaN
            continue
        crit = (i + 1) / m * alpha
        if p <= crit:
            pass_cutoff = i
    for i, c in enumerate(ranked):
        c['passes_bh'] = i <= pass_cutoff
        c['bh_rank'] = i + 1
        c['bh_m'] = m
    return ranked


def analyze_feature(trades: pd.DataFrame, feature: str, bins: int = 4, min_n: int = 8) -> dict:
    """Bucket `feature` into quantile bins and report per-bucket stats.

    Returns:
      { 'feature': name, 'overall_avg': float, 'effect': float,
        'best_bucket': {'edges', 'n', 'wr', 'avg', 'total', 't_vs_rest'},
        'worst_bucket': same shape,
        'all_buckets': [...],
        'sample_too_thin': bool }
    """
    if feature not in trades.columns:
        return {'feature': feature, 'error': 'missing column'}
    s = trades[feature]
    valid = trades[s.notna()].copy()
    if len(valid) < min_n * 2:
        return {'feature': feature, 'sample_too_thin': True, 'n_valid': len(valid)}

    try:
        # Use qcut to make equal-size buckets; falls back to cut if degenerate
        valid['_bucket'] = pd.qcut(valid[feature], q=bins, duplicates='drop')
    except ValueError:
        return {'feature': feature, 'error': 'cant bucket'}

    overall = _bucket_stats(valid)
    bucket_stats = {}
    for bucket, sub in valid.groupby('_bucket', observed=True):
        st = _bucket_stats(sub)
        st['edges'] = (float(bucket.left), float(bucket.right))
        st['t_vs_rest'] = _t_stat(
            sub['pnl_per_contract'].dropna().values,
            valid.loc[valid['_bucket'] != bucket, 'pnl_per_contract'].dropna().values
        )
        bucket_stats[str(bucket)] = st

    # Best / worst by avg P/L among buckets with n >= min_n
    ranked = [(k, v) for k, v in bucket_stats.items() if v['n'] >= min_n]
    if not ranked:
        return {'feature': feature, 'sample_too_thin': True}
    ranked.sort(key=lambda kv: kv[1]['avg'])
    worst_key, worst = ranked[0]
    best_key, best = ranked[-1]

    return {
        'feature': feature,
        'overall_avg': overall['avg'],
        'overall_n': overall['n'],
        'effect': _effect_size(bucket_stats, overall['avg']),
        'best_bucket': {'label': best_key, **best},
        'worst_bucket': {'label': worst_key, **worst},
        'all_buckets': bucket_stats,
    }


def scan_narrow_windows(trades: pd.DataFrame, feature: str, min_n: int = 15,
                        width_fracs: tuple = (0.08, 0.15, 0.25),
                        coverage: tuple = (0.02, 0.98)) -> list[dict]:
    """Slide narrow windows across the feature's value range. For each window:
    compute (n, avg, wr, t, pval) and return as a candidate. Used to find
    sharp narrow buckets that quartile bucketing misses (e.g. ret_14d ∈ [0, 0.05]).

    width_fracs: window widths as a fraction of the [p2, p98] span
    coverage: percentile pair defining the scan range (trims extreme outliers)
    """
    if feature not in trades.columns:
        return []
    s = trades[feature]
    valid = trades[s.notna()].copy()
    if len(valid) < min_n * 2:
        return []
    vmin = float(valid[feature].quantile(coverage[0]))
    vmax = float(valid[feature].quantile(coverage[1]))
    span = vmax - vmin
    if span <= 0:
        return []
    out = []
    for w_frac in width_fracs:
        w = span * w_frac
        if w <= 0:
            continue
        step = max(w / 2.0, span * 0.01)
        x = vmin
        while x + w <= vmax + 1e-9:
            mask = (valid[feature] >= x) & (valid[feature] <= x + w)
            n = int(mask.sum())
            if n >= min_n and (len(valid) - n) >= min_n:
                in_pnl = valid.loc[mask, 'pnl_per_contract'].dropna().values
                out_pnl = valid.loc[~mask, 'pnl_per_contract'].dropna().values
                t, p = _t_pval(in_pnl, out_pnl)
                out.append({
                    'feature': feature,
                    'lo': float(x), 'hi': float(x + w),
                    'width_frac': w_frac,
                    'n': n,
                    'avg': float(in_pnl.mean()) if len(in_pnl) else float('nan'),
                    'wr': float((in_pnl > 0).mean() * 100) if len(in_pnl) else float('nan'),
                    'total': float(in_pnl.sum()) if len(in_pnl) else 0.0,
                    't': t,
                    'pval': p,
                })
            x += step
    return out


def scan_pair_interactions(trades: pd.DataFrame, feat_a: str, feat_b: str,
                            grid: int = 3, min_n: int = 10) -> list[dict]:
    """For a feature pair, build a grid×grid quantile-bucket grid and return
    the cell stats. Used for 2-feature interaction analysis — finds
    conjunctions like 'iv_rank ∈ Q1 AND ret_14d ∈ Q4' that univariate
    bucketing can't surface.
    """
    if feat_a not in trades.columns or feat_b not in trades.columns:
        return []
    valid = trades[trades[feat_a].notna() & trades[feat_b].notna()].copy()
    if len(valid) < min_n * 4:
        return []
    try:
        valid['_bucket_a'] = pd.qcut(valid[feat_a], q=grid, duplicates='drop')
        valid['_bucket_b'] = pd.qcut(valid[feat_b], q=grid, duplicates='drop')
    except ValueError:
        return []
    out = []
    overall_pnl = valid['pnl_per_contract'].dropna().values
    for (ba, bb), sub in valid.groupby(['_bucket_a', '_bucket_b'], observed=True):
        if len(sub) < min_n:
            continue
        in_pnl = sub['pnl_per_contract'].dropna().values
        rest_pnl = valid.loc[~((valid['_bucket_a'] == ba) & (valid['_bucket_b'] == bb)),
                              'pnl_per_contract'].dropna().values
        t, p = _t_pval(in_pnl, rest_pnl)
        out.append({
            'feat_a': feat_a, 'feat_b': feat_b,
            'lo_a': float(ba.left), 'hi_a': float(ba.right),
            'lo_b': float(bb.left), 'hi_b': float(bb.right),
            'n': int(len(sub)),
            'avg': float(in_pnl.mean()),
            'wr': float((in_pnl > 0).mean() * 100),
            'total': float(in_pnl.sum()),
            't': t, 'pval': p,
        })
    return out


def _format_pair_rule_sketch(ticker: str, cell: dict) -> str:
    safe_a = cell['feat_a'].replace('-', '_')
    safe_b = cell['feat_b'].replace('-', '_')
    rule_name = (f"{ticker.lower()}_skip_{safe_a}_x_{safe_b}"
                 f"_{cell['lo_a']:+.2f}_{cell['hi_a']:+.2f}_{cell['lo_b']:+.2f}_{cell['hi_b']:+.2f}"
                ).replace('.', 'p').replace('+', '').replace('-', 'n')
    return f"""def _rule_{rule_name}(row, cfg, current):
    if cfg.ticker != '{ticker}':
        return {{}}
    a = row.get('{cell['feat_a']}')
    b = row.get('{cell['feat_b']}')
    if a is None or b is None or not (a == a) or not (b == b):
        return {{}}
    if {cell['lo_a']:.4f} <= a <= {cell['hi_a']:.4f} and {cell['lo_b']:.4f} <= b <= {cell['hi_b']:.4f}:
        return {{'skip': True}}
    return {{}}
ADAPTIVE_RULES['{rule_name}'] = _rule_{rule_name}"""


def analyze_custom_edges(trades: pd.DataFrame, feature: str, edges: list[float],
                          min_n: int = 8) -> dict:
    """Use explicit cut points (rather than quantiles) for `feature`. Returns
    same shape as analyze_feature."""
    if feature not in trades.columns:
        return {'feature': feature, 'error': 'missing column'}
    s = trades[feature]
    valid = trades[s.notna()].copy()
    if len(valid) < min_n * 2:
        return {'feature': feature, 'sample_too_thin': True, 'n_valid': len(valid)}
    sorted_edges = sorted(set(float(e) for e in edges))
    if len(sorted_edges) < 2:
        return {'feature': feature, 'error': 'need at least 2 edges'}
    try:
        valid['_bucket'] = pd.cut(valid[feature], bins=sorted_edges, include_lowest=True)
    except ValueError as e:
        return {'feature': feature, 'error': f'cut failed: {e}'}
    overall = _bucket_stats(valid)
    bucket_stats = {}
    for bucket, sub in valid.groupby('_bucket', observed=True):
        st = _bucket_stats(sub)
        st['edges'] = (float(bucket.left), float(bucket.right))
        st['t_vs_rest'] = _t_stat(
            sub['pnl_per_contract'].dropna().values,
            valid.loc[valid['_bucket'] != bucket, 'pnl_per_contract'].dropna().values
        )
        bucket_stats[str(bucket)] = st
    ranked = [(k, v) for k, v in bucket_stats.items() if v['n'] >= min_n]
    if not ranked:
        return {'feature': feature, 'sample_too_thin': True}
    ranked.sort(key=lambda kv: kv[1]['avg'])
    worst_key, worst = ranked[0]
    best_key, best = ranked[-1]
    return {
        'feature': feature,
        'overall_avg': overall['avg'],
        'overall_n': overall['n'],
        'effect': _effect_size(bucket_stats, overall['avg']),
        'best_bucket': {'label': best_key, **best},
        'worst_bucket': {'label': worst_key, **worst},
        'all_buckets': bucket_stats,
    }


def _format_rule_sketch(ticker: str, feature: str, bucket_label: str, bucket: dict, side_hint: str = 'skip') -> str:
    """Produce a copy-pasteable rule sketch in v1.11 hook syntax.

    `side_hint`: 'skip' (default), 'lower_delta', 'shorter_dte' — the kind of
    adjustment to apply at the worst bucket. We only emit 'skip' rules in v1
    since they need no parameter sweep beyond enabled/disabled.
    """
    lo, hi = bucket['edges']
    safe_feat = feature.replace('-', '_')
    rule_name = f"{ticker.lower()}_skip_{safe_feat}_{lo:+.2f}_{hi:+.2f}".replace('.', 'p').replace('+', '').replace('-', 'n')
    return f"""def _rule_{rule_name}(row, cfg, current):
    if cfg.ticker != '{ticker}':
        return {{}}
    v = row.get('{feature}')
    if v is None or not (v == v):  # NaN guard
        return {{}}
    if {lo:.4f} <= v <= {hi:.4f}:
        return {{'skip': True}}
    return {{}}
ADAPTIVE_RULES['{rule_name}'] = _rule_{rule_name}"""


def report_one(ticker: str, features: list[str], top_n: int = 10, bins: int = 4, min_n: int = 8,
               custom_edges: dict | None = None, scan_narrow: bool = False,
               narrow_min_n: int = 15, alpha: float = 0.05,
               pairs: bool = False, pair_grid: int = 3, pair_min_n: int = 10,
               pair_features: list[str] | None = None) -> None:
    cfg = get_config(ticker)
    df = build(ticker, period='5y')
    bt = Backtester(df=df, config=cfg, entry_fn=pick_entry, exit_fn=check_exits, ticker=ticker,
                    roll_fn=pick_roll if cfg.roll_on_max_loss else None)
    bt.run()
    trades_df = trades_to_dataframe(bt.trades)
    if trades_df.empty:
        print(f"=== {ticker}: no trades ==="); return

    feat_cols = list(set(features) - {f for f in features if f.startswith('peek_')})
    # Always include columns needed for peek calc
    feat_panel = df[[c for c in feat_cols if c in df.columns] + ['close']].copy()
    trades_aug = _attach_features(trades_df, feat_panel, cfg)

    print(f"\n=== {ticker} — {len(trades_aug)} trades — feature analysis ===")
    overall_pnl = trades_aug['pnl_per_contract']
    print(f"Overall: n={len(trades_aug)}  avg=${overall_pnl.mean():+.1f}  wr={(overall_pnl>0).mean()*100:.1f}%  std=${overall_pnl.std():.1f}")
    print()

    results = []
    for feat in features:
        if custom_edges and feat in custom_edges:
            r = analyze_custom_edges(trades_aug, feat, custom_edges[feat], min_n=min_n)
        else:
            r = analyze_feature(trades_aug, feat, bins=bins, min_n=min_n)
        if 'error' in r or r.get('sample_too_thin'):
            continue
        results.append(r)

    # Rank by effect size
    results.sort(key=lambda r: r['effect'], reverse=True)

    print(f"--- top {min(top_n, len(results))} features by effect size (max bucket avg - min bucket avg) ---\n")
    print(f"{'feature':22s}  {'effect $':>9s}  {'worst_bucket':>22s}  {'n':>4s}  {'avg':>7s}  {'wr%':>5s}  {'t':>5s}  | {'best_bucket':>22s}  {'n':>4s}  {'avg':>7s}  {'wr%':>5s}  {'t':>5s}")
    print("-" * 160)
    for r in results[:top_n]:
        w = r['worst_bucket']; b = r['best_bucket']
        print(f"{r['feature']:22s}  ${r['effect']:>+7.1f}  "
              f"{w['label']:>22s}  {w['n']:>4d}  ${w['avg']:>+5.1f}  {w['wr']:>4.0f}%  {w['t_vs_rest']:>+4.2f}  | "
              f"{b['label']:>22s}  {b['n']:>4d}  ${b['avg']:>+5.1f}  {b['wr']:>4.0f}%  {b['t_vs_rest']:>+4.2f}")

    # Emit candidate rule sketches for the strongest WORST buckets (skip rules — most conservative)
    print(f"\n--- candidate 'skip' rules (worst buckets, sorted by negative P/L impact) ---")
    skip_candidates = [r for r in results if r['worst_bucket']['avg'] < 0]
    skip_candidates.sort(key=lambda r: r['worst_bucket']['avg'])
    for r in skip_candidates[:top_n]:
        w = r['worst_bucket']
        flag = ' ⚠ small n' if w['n'] < 20 else ''
        flag += '  ⚠ weak t' if abs(w.get('t_vs_rest', 0)) < 1.5 else ''
        print(f"\n# {r['feature']}: worst bucket {w['label']} → n={w['n']}, avg=${w['avg']:+.1f}, wr={w['wr']:.0f}%, t={w['t_vs_rest']:+.2f}{flag}")
        print(_format_rule_sketch(ticker, r['feature'], w['label'], w))

    if scan_narrow:
        print(f"\n--- narrow-window scan (sliding 8%/15%/25% windows, BH-FDR @ α={alpha}) ---")
        all_candidates = []
        for feat in features:
            cands = scan_narrow_windows(trades_aug, feat, min_n=narrow_min_n)
            all_candidates.extend(cands)
        # Apply BH-FDR across the combined family of tests
        all_candidates = _bh_correct(all_candidates, alpha=alpha)
        # Sort negative-bucket candidates by t-stat (most negative first = strongest skip signal)
        neg = [c for c in all_candidates if c.get('avg', 0.0) < 0 and c.get('t', 0.0) < 0]
        neg.sort(key=lambda c: c.get('t', 0.0))
        print(f"  total candidates tested: {len(all_candidates)}  |  negative-avg candidates: {len(neg)}")
        print(f"  {'feature':22s}  {'lo':>8s}  {'hi':>8s}  {'n':>4s}  {'avg':>7s}  {'wr%':>5s}  {'t':>6s}  {'p':>7s}  {'bh':>3s}")
        print("  " + "-" * 90)
        kept = 0
        for c in neg[:top_n]:
            bh = '✓' if c.get('passes_bh') else ' '
            print(f"  {c['feature']:22s}  {c['lo']:>+8.3f}  {c['hi']:>+8.3f}  {c['n']:>4d}  "
                  f"${c['avg']:>+5.1f}  {c['wr']:>4.0f}%  {c['t']:>+6.2f}  {c['pval']:>7.4f}  {bh:>3s}")
            kept += 1
        if kept == 0:
            print("  (none — no negative narrow windows with sufficient n)")

        # Emit rule sketches for BH-significant candidates
        bh_passers = [c for c in neg if c.get('passes_bh')]
        if bh_passers:
            print(f"\n--- BH-significant narrow-window rule sketches ({len(bh_passers)}) ---")
            for c in bh_passers[:top_n]:
                bucket = {'edges': (c['lo'], c['hi']), 'n': c['n'], 'avg': c['avg'],
                          'wr': c['wr'], 't_vs_rest': c['t']}
                label = f"({c['lo']:.3f}, {c['hi']:.3f}]"
                print(f"\n# {c['feature']}: narrow bucket {label} → n={c['n']}, avg=${c['avg']:+.1f}, "
                      f"wr={c['wr']:.0f}%, t={c['t']:+.2f}, p={c['pval']:.4f}")
                print(_format_rule_sketch(ticker, c['feature'], label, bucket))
        else:
            print(f"\n(no narrow window passed BH-FDR @ α={alpha} — try --alpha 0.10 for exploratory or rely on quartile candidates)")

    if pairs:
        scan_feats = pair_features if pair_features else [f for f in features if f in trades_aug.columns]
        scan_feats = [f for f in scan_feats if trades_aug[f].notna().sum() >= pair_min_n * 4]
        # Cap pairs scanned to keep runtime bounded
        max_pairs = 50
        n_feats = len(scan_feats)
        n_pairs = n_feats * (n_feats - 1) // 2
        if n_pairs > max_pairs and not pair_features:
            print(f"\n--- 2-feature interaction scan (skipped: {n_pairs} pairs > {max_pairs} cap — pass --pair-features feat1,feat2,... to focus) ---")
        else:
            print(f"\n--- 2-feature interaction scan ({n_pairs} pairs, {pair_grid}×{pair_grid} grid, BH-FDR @ α={alpha}) ---")
            all_cells = []
            for i, fa in enumerate(scan_feats):
                for fb in scan_feats[i+1:]:
                    cells = scan_pair_interactions(trades_aug, fa, fb, grid=pair_grid, min_n=pair_min_n)
                    all_cells.extend(cells)
            all_cells = _bh_correct(all_cells, alpha=alpha)
            neg = [c for c in all_cells if c.get('avg', 0.0) < 0 and c.get('t', 0.0) < 0]
            neg.sort(key=lambda c: c.get('t', 0.0))
            print(f"  total cells tested: {len(all_cells)}  |  negative-avg cells: {len(neg)}")
            if neg:
                print(f"  {'feat_a':16s} {'rng_a':>16s}  {'feat_b':16s} {'rng_b':>16s}  {'n':>4s}  {'avg':>7s}  {'wr%':>4s}  {'t':>6s}  {'p':>7s}  {'bh':>3s}")
                print("  " + "-" * 120)
                for c in neg[:top_n]:
                    bh = '✓' if c.get('passes_bh') else ' '
                    rng_a = f"[{c['lo_a']:+.3f},{c['hi_a']:+.3f}]"
                    rng_b = f"[{c['lo_b']:+.3f},{c['hi_b']:+.3f}]"
                    print(f"  {c['feat_a']:16s} {rng_a:>16s}  {c['feat_b']:16s} {rng_b:>16s}  {c['n']:>4d}  "
                          f"${c['avg']:>+5.1f}  {c['wr']:>3.0f}%  {c['t']:>+6.2f}  {c['pval']:>7.4f}  {bh:>3s}")
                bh_passers = [c for c in neg if c.get('passes_bh')]
                if bh_passers:
                    print(f"\n--- BH-significant pair rule sketches ({len(bh_passers)}) ---")
                    for c in bh_passers[:top_n]:
                        print(f"\n# pair ({c['feat_a']} × {c['feat_b']}): "
                              f"a∈[{c['lo_a']:+.3f},{c['hi_a']:+.3f}] b∈[{c['lo_b']:+.3f},{c['hi_b']:+.3f}] "
                              f"→ n={c['n']}, avg=${c['avg']:+.1f}, t={c['t']:+.2f}, p={c['pval']:.4f}")
                        print(_format_pair_rule_sketch(ticker, c))
                else:
                    print(f"\n  (no pair passed BH-FDR @ α={alpha})")
            else:
                print("  (no negative-avg cells)")


def _parse_custom_edges(s: str) -> dict[str, list[float]]:
    """Parse --custom-edges 'feature:v1,v2,v3;feature2:v1,v2'."""
    out: dict[str, list[float]] = {}
    if not s:
        return out
    for spec in s.split(';'):
        spec = spec.strip()
        if not spec:
            continue
        if ':' not in spec:
            raise ValueError(f"bad --custom-edges spec '{spec}': expected feature:v1,v2,...")
        feat, vals = spec.split(':', 1)
        out[feat.strip()] = [float(v) for v in vals.split(',') if v.strip()]
    return out


def main():
    ap = argparse.ArgumentParser(description="v1.13 — automated rule-proposer for the critic loop.")
    ap.add_argument('--tickers', nargs='+', default=['TSLA', 'TSLL'])
    ap.add_argument('--features', help='comma-separated feature subset (default: all)')
    ap.add_argument('--top', type=int, default=10, help='show top-N features and candidate rules')
    ap.add_argument('--bins', type=int, default=4, help='quantile bin count (default 4)')
    ap.add_argument('--min-n', type=int, default=8, help='min trades per bucket to consider (default 8)')
    ap.add_argument('--custom-edges', default='',
                    help="explicit cut points per feature, e.g. 'ret_14d:-0.1,0,0.05,0.15;iv_rank:30,60'")
    ap.add_argument('--scan-narrow', action='store_true',
                    help='sliding-window scan over each feature value range with BH-FDR correction')
    ap.add_argument('--narrow-min-n', type=int, default=15,
                    help='min trades inside a narrow window (default 15)')
    ap.add_argument('--alpha', type=float, default=0.05,
                    help='BH-FDR significance level for narrow-window scan (default 0.05)')
    ap.add_argument('--pairs', action='store_true',
                    help='also run 2-feature interaction scan over feature pairs')
    ap.add_argument('--pair-grid', type=int, default=3,
                    help='grid resolution for pair scan (default 3 → 3×3 = 9 cells)')
    ap.add_argument('--pair-min-n', type=int, default=10,
                    help='min trades per pair-cell (default 10)')
    ap.add_argument('--pair-features',
                    help='comma-separated feature subset for pair scan (default: use --features)')
    args = ap.parse_args()

    features = args.features.split(',') if args.features else DEFAULT_FEATURES
    custom_edges = _parse_custom_edges(args.custom_edges)
    pair_features = args.pair_features.split(',') if args.pair_features else None
    for t in args.tickers:
        report_one(t, features, top_n=args.top, bins=args.bins, min_n=args.min_n,
                   custom_edges=custom_edges, scan_narrow=args.scan_narrow,
                   narrow_min_n=args.narrow_min_n, alpha=args.alpha,
                   pairs=args.pairs, pair_grid=args.pair_grid, pair_min_n=args.pair_min_n,
                   pair_features=pair_features)

    print("\n" + "=" * 80)
    print("Next step: pick a candidate, drop it into strategies.ADAPTIVE_RULES,")
    print("           add the rule name to DEFAULT_CONFIG_BY_TICKER[ticker]['adaptive_rules'],")
    print("           then validate with: `just backtest`, `just scenarios`, `just optimize --static`")
    return 0


if __name__ == "__main__":
    sys.exit(main())
