#!/usr/bin/env python3
"""Train-only recent-downside-shock stand-aside discovery lab.

BUILD/L0 only. The script evaluates underlying close-path downside hazard before
any option pricing and preserves the final chronological 40% of episode
blueprints outcome-unread.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

try:
    from scripts.low_hv_cross_section_train_lab import (
        assemble_close_panel,
        load_adjusted_history,
    )
except ModuleNotFoundError as exc:
    if exc.name != "scripts":
        raise
    from low_hv_cross_section_train_lab import (  # type: ignore[no-redef]
        assemble_close_panel,
        load_adjusted_history,
    )


DEFAULT_SYMBOLS = ["AAPL", "MU", "AMD", "SMCI", "TSLA", "META", "GOOGL", "NVDA"]


def _validate_panel(close_panel: pd.DataFrame) -> pd.DataFrame:
    if close_panel.empty or "SPY" not in close_panel.columns:
        raise ValueError("close panel must contain SPY and at least one candidate symbol")
    prepared = close_panel.copy()
    prepared.index = pd.DatetimeIndex(pd.to_datetime(prepared.index)).tz_localize(None).normalize()
    prepared.columns = [str(column).strip().upper() for column in prepared.columns]
    prepared = prepared.apply(pd.to_numeric, errors="coerce")
    values = prepared.to_numpy(dtype=float)
    if (
        not prepared.index.is_unique
        or not prepared.index.is_monotonic_increasing
        or len(set(prepared.columns)) != len(prepared.columns)
        or not np.isfinite(values).all()
        or (values <= 0.0).any()
    ):
        raise ValueError("close panel must be unique, increasing, finite, and positive")
    return prepared


def build_episode_blueprints(
    close_panel: pd.DataFrame,
    *,
    symbols: list[str],
    trend_lookback_sessions: int = 100,
    momentum_lookback_sessions: int = 60,
    forward_sessions: int = 10,
    shock_threshold: float = -0.03,
) -> list[dict[str, Any]]:
    """Freeze non-overlapping base-regime episodes without reading outcomes."""
    panel = _validate_panel(close_panel)
    normalized_symbols = [str(symbol).strip().upper() for symbol in symbols]
    if not normalized_symbols or any(symbol == "SPY" or symbol not in panel.columns for symbol in normalized_symbols):
        raise ValueError("candidate symbols must be non-empty panel columns other than SPY")
    if min(trend_lookback_sessions, momentum_lookback_sessions, forward_sessions) < 1:
        raise ValueError("lookbacks and forward horizon must be positive")
    if not -1.0 < shock_threshold < 0.0:
        raise ValueError("shock threshold must be a negative return fraction")

    spy = panel["SPY"]
    spy_prior_sma = spy.shift(1).rolling(
        trend_lookback_sessions, min_periods=trend_lookback_sessions
    ).mean()
    rows: list[dict[str, Any]] = []
    last_signal_position = len(panel) - forward_sessions - 2
    for symbol in normalized_symbols:
        close = panel[symbol]
        ret_1 = close / close.shift(1) - 1.0
        prior_sma = close.shift(1).rolling(
            trend_lookback_sessions, min_periods=trend_lookback_sessions
        ).mean()
        momentum = close / close.shift(momentum_lookback_sessions) - 1.0
        recent_min_return = ret_1.rolling(5, min_periods=5).min()
        stale_min_return = ret_1.shift(5).rolling(5, min_periods=5).min()
        next_available_position = 0
        for position in range(len(panel)):
            if position < next_available_position or position > last_signal_position:
                continue
            features = (
                float(spy.iloc[position]),
                float(spy_prior_sma.iloc[position]),
                float(close.iloc[position]),
                float(prior_sma.iloc[position]),
                float(momentum.iloc[position]),
                float(recent_min_return.iloc[position]),
                float(stale_min_return.iloc[position]),
            )
            if not np.isfinite(features).all():
                continue
            if not (
                features[0] > features[1]
                and features[2] > features[3]
                and features[4] > 0.0
            ):
                continue
            entry_position = position + 1
            exit_position = entry_position + forward_sessions
            rows.append(
                {
                    "symbol": symbol,
                    "signal_date": pd.Timestamp(panel.index[position]),
                    "entry_date": pd.Timestamp(panel.index[entry_position]),
                    "exit_date": pd.Timestamp(panel.index[exit_position]),
                    "spy_trend_distance": features[0] / features[1] - 1.0,
                    "symbol_trend_distance": features[2] / features[3] - 1.0,
                    "momentum_return": features[4],
                    "recent_min_return": features[5],
                    "stale_min_return": features[6],
                    "recent_shock": bool(features[5] <= shock_threshold),
                    "stale_shock": bool(features[6] <= shock_threshold),
                }
            )
            next_available_position = exit_position + 1
    return sorted(rows, key=lambda row: (row["signal_date"], row["symbol"]))


def _rate(values: np.ndarray) -> float | None:
    return float(values.mean()) if len(values) else None


def _worst_decile_mean(values: np.ndarray) -> float | None:
    if not len(values):
        return None
    count = max(1, int(np.ceil(len(values) * 0.10)))
    return float(np.sort(values)[:count].mean())


def _circular_block_rate_edge_lower_bound(
    eligible_breaches: np.ndarray,
    shock_breaches: np.ndarray,
    *,
    samples: int,
    block_length: int,
    seed: int,
    confidence: float = 0.90,
) -> float | None:
    eligible = np.asarray(eligible_breaches, dtype=float)
    shock = np.asarray(shock_breaches, dtype=float)
    if not len(eligible) or not len(shock):
        return None
    if samples < 100 or block_length < 1 or not 0.5 < confidence < 1.0:
        raise ValueError("bootstrap configuration is invalid")
    if not np.isfinite(eligible).all() or not np.isfinite(shock).all():
        raise ValueError("bootstrap inputs must be finite")
    rng = np.random.default_rng(seed)
    estimates = np.empty(samples, dtype=float)
    for sample in range(samples):
        group_means: list[float] = []
        for values in (eligible, shock):
            block = min(block_length, len(values))
            n_blocks = int(np.ceil(len(values) / block))
            starts = rng.integers(0, len(values), size=n_blocks)
            draw = np.concatenate(
                [values[(start + np.arange(block)) % len(values)] for start in starts]
            )[: len(values)]
            group_means.append(float(draw.mean()))
        estimates[sample] = group_means[1] - group_means[0]
    return float(np.quantile(estimates, 1.0 - confidence))


def evaluate_train_partition(
    close_panel: pd.DataFrame,
    train_blueprints: list[dict[str, Any]],
    *,
    min_eligible_episodes: int = 120,
    min_shock_episodes: int = 40,
    min_symbols: int = 6,
    barrier_return: float = -0.05,
    max_eligible_breach_rate: float = 0.10,
    min_breach_rate_edge: float = 0.05,
    round_trip_cost_bps: float = 20.0,
    bootstrap_samples: int = 10_000,
    bootstrap_block_length: int = 5,
) -> dict[str, Any]:
    """Evaluate only frozen train outcomes under the predeclared tail-hazard gate."""
    panel = _validate_panel(close_panel)
    if not train_blueprints or min(min_eligible_episodes, min_shock_episodes, min_symbols) < 1:
        raise ValueError("non-empty blueprints and positive density gates are required")
    if not -1.0 < barrier_return < 0.0:
        raise ValueError("barrier return must be negative")
    if not 0.0 <= max_eligible_breach_rate <= 1.0 or not 0.0 <= min_breach_rate_edge <= 1.0:
        raise ValueError("breach-rate gates must be fractions")
    if not np.isfinite(round_trip_cost_bps) or round_trip_cost_bps < 0.0:
        raise ValueError("round-trip cost must be finite and non-negative")

    rows: list[dict[str, Any]] = []
    integrity_violations: list[str] = []
    occupied: dict[str, list[tuple[pd.Timestamp, pd.Timestamp]]] = {}
    for episode_index, blueprint in enumerate(train_blueprints):
        symbol = str(blueprint["symbol"]).upper()
        signal_date = pd.Timestamp(blueprint["signal_date"])
        entry_date = pd.Timestamp(blueprint["entry_date"])
        exit_date = pd.Timestamp(blueprint["exit_date"])
        if symbol not in panel.columns:
            integrity_violations.append(f"episode_{episode_index}:missing_symbol")
            continue
        if not signal_date < entry_date < exit_date:
            integrity_violations.append(f"episode_{episode_index}:chronology")
            continue
        symbol_occupied = occupied.setdefault(symbol, [])
        if any(not (exit_date < start or entry_date > end) for start, end in symbol_occupied):
            integrity_violations.append(f"episode_{episode_index}:overlap")
            continue
        path = panel.loc[entry_date:exit_date, symbol].astype(float)
        if len(path) < 2 or path.index[0] != entry_date or path.index[-1] != exit_date:
            integrity_violations.append(f"episode_{episode_index}:path_coverage")
            continue
        entry = float(path.iloc[0])
        minimum_return = float(path.min() / entry - 1.0)
        terminal_return_after_cost = float(path.iloc[-1] / entry - 1.0 - round_trip_cost_bps / 10_000.0)
        if not np.isfinite([minimum_return, terminal_return_after_cost]).all():
            integrity_violations.append(f"episode_{episode_index}:nonfinite_outcome")
            continue
        rows.append(
            {
                "symbol": symbol,
                "signal_date": str(signal_date.date()),
                "entry_date": str(entry_date.date()),
                "exit_date": str(exit_date.date()),
                "recent_shock": bool(blueprint["recent_shock"]),
                "stale_shock": bool(blueprint["stale_shock"]),
                "minimum_close_return": minimum_return,
                "terminal_return_after_cost": terminal_return_after_cost,
                "barrier_breached": bool(minimum_return <= barrier_return),
            }
        )
        symbol_occupied.append((entry_date, exit_date))

    def group(shock_key: str, shock_value: bool) -> list[dict[str, Any]]:
        return [row for row in rows if bool(row[shock_key]) is shock_value]

    eligible = group("recent_shock", False)
    recent_shock = group("recent_shock", True)
    stale_eligible = group("stale_shock", False)
    stale_shock = group("stale_shock", True)

    def values(group_rows: list[dict[str, Any]], field: str) -> np.ndarray:
        return np.asarray([row[field] for row in group_rows], dtype=float)

    eligible_breaches = values(eligible, "barrier_breached")
    recent_breaches = values(recent_shock, "barrier_breached")
    stale_eligible_breaches = values(stale_eligible, "barrier_breached")
    stale_shock_breaches = values(stale_shock, "barrier_breached")
    eligible_rate = _rate(eligible_breaches)
    recent_rate = _rate(recent_breaches)
    stale_eligible_rate = _rate(stale_eligible_breaches)
    stale_shock_rate = _rate(stale_shock_breaches)
    current_edge = None if eligible_rate is None or recent_rate is None else recent_rate - eligible_rate
    stale_edge = (
        None
        if stale_eligible_rate is None or stale_shock_rate is None
        else stale_shock_rate - stale_eligible_rate
    )
    edge_lb90 = _circular_block_rate_edge_lower_bound(
        eligible_breaches,
        recent_breaches,
        samples=bootstrap_samples,
        block_length=bootstrap_block_length,
        seed=20260715,
    )
    eligible_tail = _worst_decile_mean(values(eligible, "minimum_close_return"))
    recent_tail = _worst_decile_mean(values(recent_shock, "minimum_close_return"))
    eligible_terminal = _rate(values(eligible, "terminal_return_after_cost"))
    eligible_symbols = sorted({row["symbol"] for row in eligible})
    shock_symbols = sorted({row["symbol"] for row in recent_shock})

    gate_checks = {
        "minimum_eligible_episodes": len(eligible) >= min_eligible_episodes,
        "minimum_recent_shock_episodes": len(recent_shock) >= min_shock_episodes,
        "minimum_eligible_symbol_breadth": len(eligible_symbols) >= min_symbols,
        "minimum_recent_shock_symbol_breadth": len(shock_symbols) >= min_symbols,
        "eligible_breach_rate_at_most_limit": eligible_rate is not None and eligible_rate <= max_eligible_breach_rate,
        "recent_shock_breach_rate_edge_at_least_minimum": current_edge is not None and current_edge >= min_breach_rate_edge,
        "recent_shock_edge_bootstrap_lb90_positive": edge_lb90 is not None and edge_lb90 > 0.0,
        "eligible_tail_less_severe": eligible_tail is not None and recent_tail is not None and eligible_tail > recent_tail,
        "eligible_terminal_mean_after_cost_positive": eligible_terminal is not None and eligible_terminal > 0.0,
        "current_filter_edge_exceeds_stale_placebo": current_edge is not None and stale_edge is not None and current_edge > stale_edge,
        "zero_integrity_violations": not integrity_violations,
    }
    return {
        "n_episodes": len(rows),
        "n_eligible_episodes": len(eligible),
        "n_recent_shock_episodes": len(recent_shock),
        "eligible_symbols": eligible_symbols,
        "recent_shock_symbols": shock_symbols,
        "eligible_breach_rate": eligible_rate,
        "recent_shock_breach_rate": recent_rate,
        "recent_shock_breach_rate_edge": current_edge,
        "recent_shock_edge_bootstrap_lb90": edge_lb90,
        "eligible_worst_decile_mean_min_return": eligible_tail,
        "recent_shock_worst_decile_mean_min_return": recent_tail,
        "eligible_mean_terminal_return_after_cost": eligible_terminal,
        "stale_eligible_breach_rate": stale_eligible_rate,
        "stale_shock_breach_rate": stale_shock_rate,
        "stale_shock_breach_rate_edge": stale_edge,
        "round_trip_underlying_cost_bps": round_trip_cost_bps,
        "barrier_return": barrier_return,
        "bootstrap_samples": bootstrap_samples,
        "bootstrap_block_length": bootstrap_block_length,
        "integrity_violations": integrity_violations,
        "gate_checks": gate_checks,
        "gate_pass": all(gate_checks.values()),
        "episodes": rows,
    }


def run_lab_from_panel(
    close_panel: pd.DataFrame,
    *,
    symbols: list[str],
    provenance: dict[str, Any],
    train_fraction: float = 0.60,
    trend_lookback_sessions: int = 100,
    momentum_lookback_sessions: int = 60,
    forward_sessions: int = 10,
    shock_threshold: float = -0.03,
    barrier_return: float = -0.05,
    min_eligible_episodes: int = 120,
    min_shock_episodes: int = 40,
    min_symbols: int = 6,
    max_eligible_breach_rate: float = 0.10,
    min_breach_rate_edge: float = 0.05,
    round_trip_cost_bps: float = 20.0,
    bootstrap_samples: int = 10_000,
    bootstrap_block_length: int = 5,
) -> dict[str, Any]:
    """Freeze the split, read train outcomes only, and emit a strict F0 decision."""
    panel = _validate_panel(close_panel)
    if not 0.0 < train_fraction < 1.0:
        raise ValueError("train fraction must be strictly between zero and one")
    blueprints = build_episode_blueprints(
        panel,
        symbols=symbols,
        trend_lookback_sessions=trend_lookback_sessions,
        momentum_lookback_sessions=momentum_lookback_sessions,
        forward_sessions=forward_sessions,
        shock_threshold=shock_threshold,
    )
    if len(blueprints) < 2:
        raise ValueError("at least two frozen episodes are required to reserve a holdout")
    signal_dates = sorted({pd.Timestamp(row["signal_date"]) for row in blueprints})
    if len(signal_dates) < 2:
        raise ValueError("at least two distinct signal dates are required to reserve a holdout")
    cutoff_index = min(
        len(signal_dates) - 2,
        max(0, int(np.floor(len(signal_dates) * train_fraction)) - 1),
    )
    train_cutoff = signal_dates[cutoff_index]
    train_blueprints = [row for row in blueprints if pd.Timestamp(row["signal_date"]) <= train_cutoff]
    holdout_blueprints = [row for row in blueprints if pd.Timestamp(row["signal_date"]) > train_cutoff]
    train = evaluate_train_partition(
        panel,
        train_blueprints,
        min_eligible_episodes=min_eligible_episodes,
        min_shock_episodes=min_shock_episodes,
        min_symbols=min_symbols,
        barrier_return=barrier_return,
        max_eligible_breach_rate=max_eligible_breach_rate,
        min_breach_rate_edge=min_breach_rate_edge,
        round_trip_cost_bps=round_trip_cost_bps,
        bootstrap_samples=bootstrap_samples,
        bootstrap_block_length=bootstrap_block_length,
    )
    holdout_identity = [
        {
            "symbol": row["symbol"],
            "signal_date": str(pd.Timestamp(row["signal_date"]).date()),
            "entry_date": str(pd.Timestamp(row["entry_date"]).date()),
            "exit_date": str(pd.Timestamp(row["exit_date"]).date()),
        }
        for row in holdout_blueprints
    ]
    holdout_hash = hashlib.sha256(
        json.dumps(holdout_identity, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    advanced = bool(train["gate_pass"])
    failed_gates = [name for name, passed in train["gate_checks"].items() if not passed]
    payload: dict[str, Any] = {
        "schema_version": "downside_shock_stand_aside_train_lab.v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "candidate_id": "MULTINAME_NO_RECENT_DOWNSHOCK_PCS_21D_V1",
        "strategy_outcome": "STRATEGY_ADVANCED" if advanced else "FAMILY_CLOSED",
        "funnel_before": "F0_MECHANISM",
        "funnel_after": "F1_TRAIN" if advanced else "F0_MECHANISM_CLOSED",
        "funnel_claim_f2": False,
        "l1_claim": False,
        "claim_bar": "L0_DISCOVERY_ONLY",
        "claim_scope": (
            "Train-only underlying close-path non-collapse evidence. No option pricing, "
            "credit, skew, IV, executable fill, intraday barrier, or managed-PnL claim."
        ),
        "methodology_boundaries": {
            "panel_bias_free": False,
            "panel_selection_bias": (
                "The fixed panel is a present-day liquid mega-cap/technology set plus SMCI. "
                "It has survivorship and listing-history bias and is not a point-in-time universe."
            ),
            "barrier_fidelity": (
                "The 5% endpoint uses daily closes only; it can miss intraday lows and does not "
                "represent spread marks, executable stops, or managed option PnL."
            ),
            "specificity_control": (
                "Recent-five-session and stale-six-to-ten-session shock flags are computed "
                "independently and can both be true. Their edge comparison is a confounded "
                "timing-specificity diagnostic, not a mutually exclusive alternative-mechanism RCT."
            ),
            "bootstrap_dependence": (
                "The L0 uncertainty check resamples each pooled group vector with circular blocks; "
                "it is not a multi-symbol date-blocked bootstrap and retains cross-symbol/date dependence."
            ),
        },
        "market_underlying": {
            "regime_proxy": "SPY",
            "candidate_symbols": [str(symbol).upper() for symbol in symbols],
        },
        "forecast_type": "non_collapse",
        "economic_mechanism": (
            "Downside volatility clusters; excluding new put-credit risk for five completed "
            "sessions after a >=3% close loss should reduce ten-session 5% downside-barrier hazard "
            "inside a long-term SPY-and-symbol uptrend."
        ),
        "structure": "conditional_put_credit_spread_not_yet_priced",
        "structure_plan": "one-lot 21-DTE $2-wide put credit spread",
        "option_entry_filter": {
            "expiry_selection": "nearest listed expiration inside the frozen DTE range",
            "dte_range": [18, 24],
            "short_leg": "sell one put",
            "short_put_delta_range": [0.18, 0.25],
            "long_leg": "buy one same-expiry put $2 below the short strike",
            "wing_width_usd": 2.0,
            "minimum_credit_usd": 0.30,
            "quote_quality": "both legs require positive bid and a two-leg NBBO width <= $0.20",
            "event_blackout": "stand aside within five sessions of scheduled issuer earnings",
            "status": "future paper-plan filter only; not priced or exercised at F0",
        },
        "greek_exposures": {
            "intended": ["positive delta", "positive theta", "short vega", "bounded short gamma"],
            "dangerous_unintended": [
                "gap-through-wing loss",
                "renewed downside clustering",
                "volatility/skew expansion",
                "assignment and two-leg liquidity risk",
            ],
        },
        "regime_envelope": (
            "Completed SPY and symbol closes above lag-safe prior-completed SMA100 with positive "
            "completed 60-session symbol return; invalid after a latest-five-session <=-3% close loss."
        ),
        "entry_trigger": "next session after completed signal close; non-overlapping per symbol",
        "exit_rule": (
            "Future option plan: 50% credit harvest, close after an underlying close 5% below "
            "entry, or ten-session time stop. F0 evaluates only the fixed ten-session close path."
        ),
        "stand_aside_rule": (
            "No entry below SPY/symbol SMA100, with non-positive 60-session return, after a "
            "latest-five-session <=-3% close loss, or when later quote/capital/integrity gates fail."
        ),
        "sleeve_usd": 3000.0,
        "capital_fit_usd": 200.0,
        "one_lot_max_loss_usd": 200.0,
        "max_lots": 1,
        "portfolio_overlap": "one global correlated bullish risk unit; no simultaneous panel entries",
        "data_provenance": provenance,
        "data_window": {
            "panel_start": str(panel.index[0].date()),
            "panel_end": str(panel.index[-1].date()),
            "panel_rows": int(len(panel)),
            "blueprints": len(blueprints),
            "train_blueprints": len(train_blueprints),
            "holdout_blueprints": len(holdout_blueprints),
            "train_fraction_target": train_fraction,
            "train_fraction_realized": len(train_blueprints) / len(blueprints),
            "train_last_signal_date": str(pd.Timestamp(train_blueprints[-1]["signal_date"]).date()),
        },
        "parameters": {
            "trend_lookback_sessions": trend_lookback_sessions,
            "momentum_lookback_sessions": momentum_lookback_sessions,
            "forward_sessions": forward_sessions,
            "shock_threshold": shock_threshold,
            "barrier_return": barrier_return,
            "max_eligible_breach_rate": max_eligible_breach_rate,
            "min_breach_rate_edge": min_breach_rate_edge,
            "round_trip_underlying_cost_bps": round_trip_cost_bps,
        },
        "train": train,
        "untouched_holdout": {
            "n_blueprints": len(holdout_blueprints),
            "first_signal_date": str(pd.Timestamp(holdout_blueprints[0]["signal_date"]).date()),
            "last_exit_date": str(pd.Timestamp(holdout_blueprints[-1]["exit_date"]).date()),
            "identity_sha256": holdout_hash,
            "outcome_metrics_read": False,
            "simulation_run": False,
            "opening_condition": "only a future predeclared F2 wake after F1 train advance",
        },
        "option_stage": {
            "pricing_calls": 0,
            "observed_option_marks": False,
            "proxy_option_prices": False,
            "option_cost_claim": False,
        },
        "authority": {
            "paper_intent_created": False,
            "registry_promotion": False,
            "shadow_or_live_authority": False,
        },
        "dominant_failure_mechanism": (
            None
            if advanced
            else "failed gates: " + ", ".join(failed_gates)
        ),
    }
    json.dumps(payload, allow_nan=False)
    return payload


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--symbols", default=",".join(DEFAULT_SYMBOLS))
    parser.add_argument("--start", default="2016-01-01")
    parser.add_argument("--end", default="2026-07-15")
    parser.add_argument("--cache-dir", default=".cache/platform/downside-shock-history")
    parser.add_argument("--out", required=True)
    parser.add_argument("--bootstrap-samples", type=int, default=10_000)
    args = parser.parse_args(argv)

    symbols = [value.strip().upper() for value in args.symbols.split(",") if value.strip()]
    requested = ["SPY", *symbols]
    histories: dict[str, pd.Series] = {}
    sources: dict[str, Any] = {}
    for symbol in requested:
        history, source = load_adjusted_history(
            symbol,
            cache_dir=Path(args.cache_dir),
            start=args.start,
            end=args.end,
        )
        histories[symbol] = history
        sources[symbol] = source
    panel = assemble_close_panel(histories, symbols=requested, min_common_rows=1_500)
    payload = run_lab_from_panel(
        panel,
        symbols=symbols,
        provenance={
            "provider": "yfinance",
            "adjustment_semantics": "auto_adjust=True split/dividend-adjusted close",
            "requested_start": args.start,
            "requested_end_exclusive": args.end,
            "sources": sources,
        },
        bootstrap_samples=args.bootstrap_samples,
    )
    output_path = Path(args.out)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n")
    print(json.dumps({
        "out": str(output_path),
        "strategy_outcome": payload["strategy_outcome"],
        "funnel_after": payload["funnel_after"],
        "gate_pass": payload["train"]["gate_pass"],
        "train_episodes": payload["train"]["n_episodes"],
        "holdout_blueprints": payload["untouched_holdout"]["n_blueprints"],
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
