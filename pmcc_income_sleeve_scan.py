#!/usr/bin/env python3
"""Income-sleeve PMCC scan: aggressive shorts where capped rip is acceptable."""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite

import pandas as pd

import pricing
from pmcc.chain_data import fetch_call_chain

R = 0.04
TICKER = "TSLA"
LONG_EXPS = ("2028-06-16", "2028-12-15")
SHORT_DTES = (24, 31, 38, 52, 80, 108)
LONG_STRIKES = (380, 390, 400, 410, 420, 430, 440)
SHORT_DELTA_RANGE = (0.22, 0.50)
MIN_OTM = 0.04
MAX_OTM = 0.25


@dataclass(frozen=True)
class Contract:
    exp: str
    dte: int
    strike: float
    mid: float
    bid: float
    ask: float
    iv: float
    delta: float
    spread_pct: float

    @property
    def dollars(self) -> float:
        return self.mid * 100.0


def call_value(spot: float, strike: float, dte: int, iv: float, iv_mult: float = 1.0) -> float:
    if dte <= 0:
        return max(spot - strike, 0.0)
    try:
        return max(pricing.price(spot, strike, dte / 365.0, max(iv * iv_mult, 0.01), "call", r=R), 0.0)
    except (ValueError, ZeroDivisionError):
        return max(spot - strike, 0.0)


def row_to_contract(row: pd.Series) -> Contract:
    return Contract(
        exp=str(row.expiration),
        dte=int(row.dte),
        strike=float(row.strike),
        mid=float(row.mid),
        bid=float(row.bid),
        ask=float(row.ask),
        iv=float(row.iv),
        delta=float(row.delta),
        spread_pct=float(row.spread_pct),
    )


def pnl_at_short_expiry(spot: float, long: Contract, short: Contract, basis: float, iv_mult: float) -> float:
    long_left = max(long.dte - short.dte, 1)
    long_mark = call_value(spot, long.strike, long_left, long.iv, iv_mult) * 100.0
    short_buyback = max(spot - short.strike, 0.0) * 100.0
    return long_mark + short.dollars - short_buyback - basis


def pnl_midcycle(spot: float, long: Contract, short: Contract, basis: float, days_elapsed: int, iv_mult: float) -> float:
    long_left = max(long.dte - days_elapsed, 1)
    short_left = max(short.dte - days_elapsed, 1)
    long_mark = call_value(spot, long.strike, long_left, long.iv, iv_mult) * 100.0
    short_buyback = call_value(spot, short.strike, short_left, short.iv, iv_mult) * 100.0
    return long_mark + short.dollars - short_buyback - basis


def scenario_metrics(spot: float, long: Contract, short: Contract, basis: float) -> dict[str, float]:
    down20 = pnl_at_short_expiry(spot * 0.80, long, short, basis, 1.20)
    down10 = pnl_at_short_expiry(spot * 0.90, long, short, basis, 1.12)
    flat = pnl_at_short_expiry(spot, long, short, basis, 1.00)
    up10 = pnl_at_short_expiry(spot * 1.10, long, short, basis, 0.95)
    rip500 = pnl_at_short_expiry(500.0, long, short, basis, 0.88)
    rip600 = pnl_at_short_expiry(600.0, long, short, basis, 0.82)
    rip700 = pnl_at_short_expiry(700.0, long, short, basis, 0.78)
    half = max(short.dte // 2, 1)
    mid500 = pnl_midcycle(500.0, long, short, basis, half, 0.95)
    mid_down10 = pnl_midcycle(spot * 0.90, long, short, basis, half, 1.15)
    bear_min = min(down20, down10, flat)
    rip_min = min(rip500, rip600, rip700)
    return {
        "down20": down20,
        "down10": down10,
        "flat": flat,
        "up10": up10,
        "rip500": rip500,
        "rip600": rip600,
        "rip700": rip700,
        "mid500": mid500,
        "mid_down10": mid_down10,
        "bear_min": bear_min,
        "rip_min": rip_min,
    }


def score_row(rec: dict) -> float:
    basis = rec["basis"]
    ann_income = rec["ann_income_pct"]
    flat_ret = rec["flat"] / basis * 100.0
    down10_ret = rec["down10"] / basis * 100.0
    bear_min_ret = rec["bear_min"] / basis * 100.0
    rip_min_ret = rec["rip_min"] / basis * 100.0
    mid500_ret = rec["mid500"] / basis * 100.0
    penalty = 0.0
    if rec["rip_min"] < 0:
        penalty += 200.0
    if rec["mid500"] < 0:
        penalty += 100.0
    # Income sleeve: income matters most, but reject structures that only work by hiding tail risk.
    return (
        0.45 * ann_income
        + 0.20 * flat_ret
        + 0.15 * down10_ret
        + 0.10 * bear_min_ret
        + 0.10 * rip_min_ret
        + 0.05 * mid500_ret
        - penalty
    )


def fmt_money(x: float) -> str:
    return f"${x:,.0f}"


def main() -> None:
    spot, df = fetch_call_chain(TICKER, refresh=False)
    print(f"Income-sleeve scan — {TICKER} spot ${spot:.2f}")
    print("Objective: high short income; capped rip is OK if close-both sleeve stays green; down/flat must be survivable.")
    print()

    longs: list[Contract] = []
    for exp in LONG_EXPS:
        for k in LONG_STRIKES:
            rows = df[(df.expiration == exp) & (df.strike == float(k))]
            if rows.empty:
                continue
            c = row_to_contract(rows.iloc[0])
            if c.mid > 0 and c.spread_pct <= 0.30:
                longs.append(c)

    shorts: list[Contract] = []
    for dte in SHORT_DTES:
        # exact listed DTEs are from the chain; nearest is not used because DTE is a core variable here.
        rows = df[df.dte == dte]
        for _, row in rows.iterrows():
            c = row_to_contract(row)
            otm = c.strike / spot - 1.0
            if (
                c.mid >= 1.0
                and c.bid > 0
                and c.ask > 0
                and c.spread_pct <= 0.35
                and MIN_OTM <= otm <= MAX_OTM
                and SHORT_DELTA_RANGE[0] <= c.delta <= SHORT_DELTA_RANGE[1]
            ):
                shorts.append(c)

    records: list[dict] = []
    for long in longs:
        basis = long.dollars
        for short in shorts:
            if short.strike <= long.strike + 20:
                continue
            if short.dte >= long.dte:
                continue
            credit = short.dollars
            metrics = scenario_metrics(spot, long, short, basis)
            rec = {
                "long": f"{int(long.strike)}/{long.exp}",
                "short": f"{int(short.strike)}/{short.exp}",
                "long_strike": long.strike,
                "long_exp": long.exp,
                "long_dte": long.dte,
                "short_strike": short.strike,
                "short_exp": short.exp,
                "short_dte": short.dte,
                "basis": basis,
                "credit": credit,
                "credit_day": credit / short.dte,
                "ann_income_pct": credit / basis * 365.0 / short.dte * 100.0,
                "otm_pct": (short.strike / spot - 1.0) * 100.0,
                "short_delta": short.delta,
                "long_delta": long.delta,
                **metrics,
            }
            rec["score"] = score_row(rec)
            records.append(rec)

    out = pd.DataFrame(records)
    if out.empty:
        raise SystemExit("No candidates after filters")

    viable = out[(out.rip500 > 0) & (out.rip600 > 0) & (out.rip700 > 0) & (out.mid500 > 0)].copy()
    print(f"Candidates scanned: {len(out)}; viable non-loss at $500/$600/$700 + midcycle $500: {len(viable)}")
    print()

    cols = [
        "long", "short", "basis", "credit", "credit_day", "ann_income_pct", "otm_pct", "short_delta",
        "down20", "down10", "flat", "rip500", "rip600", "rip700", "mid500", "score",
    ]
    show = viable.sort_values("score", ascending=False).head(20)[cols].copy()
    for c in ("basis", "credit", "down20", "down10", "flat", "rip500", "rip600", "rip700", "mid500"):
        show[c] = show[c].map(fmt_money)
    for c in ("credit_day", "ann_income_pct", "otm_pct", "short_delta", "score"):
        show[c] = show[c].map(lambda x: f"{x:.1f}" if c != "short_delta" else f"{x:.2f}")
    print("Top 20 viable by income-sleeve score:")
    print(show.to_string(index=False))
    print()

    # Best per short DTE, to answer DTE choice directly.
    print("Best viable candidate per short DTE:")
    rows = []
    for dte, g in viable.groupby("short_dte"):
        r = g.sort_values("score", ascending=False).iloc[0]
        rows.append(r)
    by_dte = pd.DataFrame(rows).sort_values("short_dte")[cols].copy()
    for c in ("basis", "credit", "down20", "down10", "flat", "rip500", "rip600", "rip700", "mid500"):
        by_dte[c] = by_dte[c].map(fmt_money)
    for c in ("credit_day", "ann_income_pct", "otm_pct", "short_delta", "score"):
        by_dte[c] = by_dte[c].map(lambda x: f"{x:.1f}" if c != "short_delta" else f"{x:.2f}")
    print(by_dte.to_string(index=False))
    print()

    # Existing user's high-cost 410 Jun 2028 sleeve, override basis=13000.
    print("Existing high-cost $410 Jun-2028 LEAPS sleeve, basis forced to $13,000 per contract:")
    existing_long = next(c for c in longs if c.exp == "2028-06-16" and int(c.strike) == 410)
    ex_records = []
    for short in shorts:
        if short.strike <= existing_long.strike + 20:
            continue
        rec = {
            "long": "410/2028-06-16 @ $13k basis",
            "short": f"{int(short.strike)}/{short.exp}",
            "long_strike": existing_long.strike,
            "long_exp": existing_long.exp,
            "long_dte": existing_long.dte,
            "short_strike": short.strike,
            "short_exp": short.exp,
            "short_dte": short.dte,
            "basis": 13000.0,
            "credit": short.dollars,
            "credit_day": short.dollars / short.dte,
            "ann_income_pct": short.dollars / 13000.0 * 365.0 / short.dte * 100.0,
            "otm_pct": (short.strike / spot - 1.0) * 100.0,
            "short_delta": short.delta,
            "long_delta": existing_long.delta,
            **scenario_metrics(spot, existing_long, short, 13000.0),
        }
        rec["score"] = score_row(rec)
        ex_records.append(rec)
    ex = pd.DataFrame(ex_records)
    ex_viable = ex[(ex.rip500 > 0) & (ex.rip600 > 0) & (ex.rip700 > 0) & (ex.mid500 > 0)].copy()
    ex_show = ex_viable.sort_values("score", ascending=False).head(16)[cols].copy()
    for c in ("basis", "credit", "down20", "down10", "flat", "rip500", "rip600", "rip700", "mid500"):
        ex_show[c] = ex_show[c].map(fmt_money)
    for c in ("credit_day", "ann_income_pct", "otm_pct", "short_delta", "score"):
        ex_show[c] = ex_show[c].map(lambda x: f"{x:.1f}" if c != "short_delta" else f"{x:.2f}")
    print(ex_show.to_string(index=False))

    out.to_csv(".cache/pmcc_income_sleeve_scan_TSLA.csv", index=False)
    viable.to_csv(".cache/pmcc_income_sleeve_scan_TSLA_viable.csv", index=False)
    print("\nWrote .cache/pmcc_income_sleeve_scan_TSLA.csv and _viable.csv")


if __name__ == "__main__":
    main()
