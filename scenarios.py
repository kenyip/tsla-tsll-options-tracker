#!/usr/bin/env python3
"""
Regime scenario suite.

Defines 12 canonical market regimes and a discovery routine that scans historical
data for windows matching each. Once discovered, the *fixed* canonical windows
are recorded in CANONICAL_SCENARIOS — that way `just scenarios` is reproducible
across strategy changes and runs can be compared directly.

To re-curate scenarios after data drifts (e.g. years later when TSLA's history
looks very different), run `python scenarios.py --discover` and update the
CANONICAL_SCENARIOS dict.

A single window can match multiple regimes (e.g. a huge_up window during an IV
crush is both 'huge_up' and 'vol_crush'). classify_window returns the *set* of
all matching labels.

Direction / shape regimes (return-based):
- huge_down       cumulative return < -15% over window
- normal_down     return between -15% and -5%
- flat            return in [-3%, +3%], intra-window swing < 7%
- normal_up       return in [+5%, +15%]
- huge_up         return > +15%
- v_recovery      drops > 5% in first half, recovers > 5% from low to end, net flat-ish
- inverse_v       rallies > 5% in first half, gives back > 5% from high to end

Tail / vol / event regimes (added 2026-05-12 for extreme-case management):
- gap_shock       window contains an overnight gap > 7% (|open - prev_close| / prev_close)
- vol_crush       IV rank starts high (>=60), ends low (<=30); modest net move
- vol_expansion   IV rank rises >=30 points through the window, ending >=50
- chop_whipsaw    |net return| < 5% but high-low range > 12% AND >=5 days with |ret_1d| > 3%
- earnings_window window contains a known TSLA earnings announcement date
"""

from __future__ import annotations
import argparse
from collections import defaultdict
import pandas as pd

from data import build


REGIMES = [
    'huge_down', 'normal_down', 'flat', 'normal_up', 'huge_up',
    'v_recovery', 'inverse_v',
    'gap_shock', 'vol_crush', 'vol_expansion', 'chop_whipsaw', 'earnings_window',
]
WINDOW_DAYS = 21       # ~one trading month
DISCOVERY_STEP = 5     # slide forward 5 days between candidate windows

# TSLA earnings announcement dates (after-hours). The 21-day canonical
# window is anchored 5 trading days before each date so the event lands at
# ~day 6, capturing both the pre-event IV ramp and the post-event crush.
# TSLL tracks TSLA so the same dates apply to TSLL windows.
TSLA_EARNINGS_DATES = [
    '2021-01-27', '2021-04-26', '2021-07-26', '2021-10-20',
    '2022-01-26', '2022-04-20', '2022-07-20', '2022-10-19',
    '2023-01-25', '2023-04-19', '2023-07-19', '2023-10-18',
    '2024-01-24', '2024-04-23', '2024-07-23', '2024-10-23',
    '2025-01-29', '2025-04-22', '2025-07-23', '2025-10-22',
]


# Fixed canonical scenarios — one per regime per ticker. Populated by running
# `python scenarios.py --discover` and picking representative windows. These
# stay frozen so strategy A/B comparisons are apples-to-apples.
CANONICAL_SCENARIOS = {
    'TSLA': {
        # direction / shape
        'huge_down':       ('2025-02-19', '2025-03-19'),   # -34.6%
        'normal_down':     ('2024-09-24', '2024-10-22'),   # -14.3%
        'flat':            ('2023-11-14', '2023-12-13'),   #  +0.8% (only match in 5y)
        'normal_up':       ('2024-08-12', '2024-09-10'),   # +14.5%
        'huge_up':         ('2024-10-22', '2024-11-19'),   # +58.7%
        'v_recovery':      ('2025-04-09', '2025-05-08'),   #  +4.6%
        'inverse_v':       ('2024-09-17', '2024-10-15'),   #  -3.6%
        # tail / vol / event (added 2026-05-12)
        'gap_shock':       ('2024-10-01', '2024-10-29'),   #  +0.6%  max gap +14.5%
        'vol_crush':       ('2024-05-15', '2024-06-13'),   #  +4.9%  iv_rank 97→10
        'vol_expansion':   ('2025-03-05', '2025-04-02'),   #  +1.3%  iv_rank 25→96
        'chop_whipsaw':    ('2024-02-05', '2024-03-05'),   #  -0.2%
        'earnings_window': ('2025-10-15', '2025-11-12'),   #  -1.0%  TSLA earnings 2025-10-22
    },
    'TSLL': {
        # direction / shape
        'huge_down':       ('2025-02-21', '2025-03-21'),   # -50.1%
        'normal_down':     ('2025-06-10', '2025-07-10'),   # -13.4%
        'flat':            None,                            # 2x-leverage on high-vol underlying — no flat windows exist
        'normal_up':       ('2024-08-21', '2024-09-19'),   # +14.8%
        'huge_up':         ('2024-11-14', '2024-12-13'),   # +89.0%
        'v_recovery':      ('2024-07-24', '2024-08-21'),   #  +3.1%
        'inverse_v':       ('2024-09-12', '2024-10-10'),   #  +4.8%
        # tail / vol / event (added 2026-05-12)
        'gap_shock':       ('2024-09-26', '2024-10-24'),   #  -0.9%  max gap +29.0%
        'vol_crush':       ('2023-11-24', '2023-12-22'),   #  +7.1%  iv_rank 64→4
        'vol_expansion':   ('2024-01-24', '2024-02-22'),   #  -9.2%  iv_rank 1→62
        'chop_whipsaw':    ('2025-05-12', '2025-06-10'),   #  -0.9%
        'earnings_window': ('2025-10-10', '2025-11-07'),   #  +5.1%  TSLA earnings 2025-10-22
    },
}


def _earnings_in_window(window: pd.DataFrame) -> bool:
    if len(window) == 0:
        return False
    start, end = window.index[0], window.index[-1]
    return any(start <= pd.Timestamp(d) <= end for d in TSLA_EARNINGS_DATES)


def _max_overnight_gap(window: pd.DataFrame) -> float:
    """Return the largest |open[t] - close[t-1]| / close[t-1] across the window."""
    if 'open' not in window.columns or len(window) < 2:
        return 0.0
    prev_close = window['close'].shift(1)
    gap = ((window['open'] - prev_close).abs() / prev_close).dropna()
    return float(gap.max()) if len(gap) else 0.0


def classify_window(window: pd.DataFrame) -> set[str]:
    """Return all regimes this window matches (possibly empty, possibly multiple)."""
    if len(window) < max(WINDOW_DAYS - 3, 10):
        return set()

    start_price = float(window['close'].iloc[0])
    end_price = float(window['close'].iloc[-1])
    if start_price <= 0:
        return set()

    labels: set[str] = set()
    ret = (end_price - start_price) / start_price
    mid = len(window) // 2
    first_low = float(window['close'].iloc[:mid].min())
    first_high = float(window['close'].iloc[:mid].max())
    first_low_ret = (first_low - start_price) / start_price
    first_high_ret = (first_high - start_price) / start_price
    recovery_from_low = (end_price - first_low) / first_low if first_low > 0 else 0
    drop_from_high = (first_high - end_price) / first_high if first_high > 0 else 0
    window_high = float(window['close'].max())
    window_low = float(window['close'].min())
    swing = (window_high - window_low) / start_price

    # Direction / shape (mutually exclusive — pick one)
    if first_low_ret < -0.05 and recovery_from_low > 0.05 and -0.05 < ret < 0.05:
        labels.add('v_recovery')
    elif first_high_ret > 0.05 and drop_from_high > 0.05 and -0.05 < ret < 0.05:
        labels.add('inverse_v')
    elif ret < -0.15:
        labels.add('huge_down')
    elif ret < -0.05:
        labels.add('normal_down')
    elif -0.03 <= ret <= 0.03 and swing < 0.07:
        labels.add('flat')
    elif 0.05 <= ret <= 0.15:
        labels.add('normal_up')
    elif ret > 0.15:
        labels.add('huge_up')

    # Tail / vol / event regimes (additive — can co-occur with direction)
    if _max_overnight_gap(window) > 0.07:
        labels.add('gap_shock')

    if 'iv_rank' in window.columns:
        iv_start = window['iv_rank'].iloc[0]
        iv_end = window['iv_rank'].iloc[-1]
        if pd.notna(iv_start) and pd.notna(iv_end):
            if iv_start >= 60 and iv_end <= 30:
                labels.add('vol_crush')
            if iv_end - iv_start >= 30 and iv_end >= 50:
                labels.add('vol_expansion')

    if abs(ret) < 0.05 and swing > 0.12:
        big_days = (window['close'].pct_change().abs() > 0.03).sum()
        if big_days >= 5:
            labels.add('chop_whipsaw')

    if _earnings_in_window(window):
        labels.add('earnings_window')

    return labels


def discover(df: pd.DataFrame, window_days: int = WINDOW_DAYS, step: int = DISCOVERY_STEP) -> dict:
    """Scan history; return {regime: [{'start','end','ret', extra...}, ...]}."""
    matches = defaultdict(list)
    n = len(df)
    for start in range(0, n - window_days, step):
        window = df.iloc[start:start + window_days]
        labels = classify_window(window)
        if not labels:
            continue
        s = float(window['close'].iloc[0])
        e = float(window['close'].iloc[-1])
        ret = (e - s) / s
        gap = _max_overnight_gap(window)
        iv_start = float(window['iv_rank'].iloc[0]) if 'iv_rank' in window.columns and pd.notna(window['iv_rank'].iloc[0]) else float('nan')
        iv_end = float(window['iv_rank'].iloc[-1]) if 'iv_rank' in window.columns and pd.notna(window['iv_rank'].iloc[-1]) else float('nan')
        for regime in labels:
            matches[regime].append({
                'start': window.index[0],
                'end': window.index[-1],
                'ret': ret,
                'gap': gap,
                'iv_start': iv_start,
                'iv_end': iv_end,
            })
    return dict(matches)


def canonical_window(df: pd.DataFrame, ticker: str, regime: str) -> pd.DataFrame | None:
    """Return the slice of df for the canonical (ticker, regime) window, or None."""
    spec = CANONICAL_SCENARIOS.get(ticker, {}).get(regime)
    if spec is None:
        return None
    start, end = spec
    sl = df.loc[start:end]
    return sl if len(sl) >= 10 else None


def _sort_key_for(regime: str):
    if regime == 'gap_shock':
        return lambda h: h.get('gap', 0), True
    if regime == 'vol_crush':
        return lambda h: h.get('iv_start', 0) - h.get('iv_end', 0), True
    if regime == 'vol_expansion':
        return lambda h: h.get('iv_end', 0) - h.get('iv_start', 0), True
    if regime == 'chop_whipsaw':
        return lambda h: -abs(h.get('ret', 0)), True  # smaller |ret| first
    if regime == 'earnings_window':
        return lambda h: h['start'], True
    if regime == 'flat':
        return lambda h: abs(h.get('ret', 0)), False  # smaller |ret| first
    return lambda h: abs(h.get('ret', 0)), True


def print_discovery(ticker: str, matches: dict, top_n: int = 5):
    print(f"\n=== {ticker} regime discovery ({WINDOW_DAYS}d windows, slide {DISCOVERY_STEP}d) ===")
    for regime in REGIMES:
        hits = matches.get(regime, [])
        print(f"\n{regime}  ({len(hits)} matches)")
        if not hits:
            print("  (none — consider widening band or synthetic fill)")
            continue
        key_fn, reverse = _sort_key_for(regime)
        hits_sorted = sorted(hits, key=key_fn, reverse=reverse)
        for h in hits_sorted[:top_n]:
            extra = ''
            if regime == 'gap_shock':
                extra = f"  max gap {h['gap']*100:+5.1f}%"
            elif regime in ('vol_crush', 'vol_expansion'):
                extra = f"  iv_rank {h['iv_start']:.0f}→{h['iv_end']:.0f}"
            print(f"  {h['start'].date()} → {h['end'].date()}  return = {h['ret']*100:+6.1f}%{extra}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--tickers', nargs='+', default=['TSLA', 'TSLL'])
    ap.add_argument('--period', default='5y')
    ap.add_argument('--discover', action='store_true',
                    help='print discovered candidate windows for each regime')
    args = ap.parse_args()

    for ticker in args.tickers:
        df = build(ticker, period=args.period)
        if args.discover:
            matches = discover(df)
            print_discovery(ticker, matches)
        else:
            print(f"\n=== {ticker} canonical scenarios ===")
            for regime in REGIMES:
                w = canonical_window(df, ticker, regime)
                if w is None:
                    print(f"  {regime:<12}  (no canonical window defined)")
                    continue
                ret = (w['close'].iloc[-1] - w['close'].iloc[0]) / w['close'].iloc[0]
                print(f"  {regime:<12}  {w.index[0].date()} → {w.index[-1].date()}  "
                      f"return = {ret*100:+6.1f}%  ({len(w)} bars)")


if __name__ == "__main__":
    main()
