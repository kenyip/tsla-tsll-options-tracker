"""Research loop foundation: regime → strategy → symbol → premium scout (paper-first).

Replaces M0–M1 stub proposals with real short-premium signals from live.make_recommendation
(same pick_entry path as backtest). Default consumer is autonomy_loop paper/shadow modes.

Pipeline stages
--------------
1. REGIME   — features from data.build (regime, iv_rank, high_iv, reversal)
2. STRATEGY — eligible hypotheses from registry (premium sleeve; status testing|paper|shadow|live)
3. SYMBOL   — instruments on each hypothesis, ranked by scout fitness
4. PREMIUM  — live.make_recommendation → OrderIntent or stand-aside
5. PAPER    — caller (autonomy_loop) risk-checks and paper-executes; this module never places live

Stand-aside is success (logged, not a failed scout).
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Iterable, Optional, Sequence

from trader_platform.hypothesis_registry import Hypothesis, HypothesisRegistry
from trader_platform.risk_governor import OrderIntent

_REPO = Path(__file__).resolve().parents[1]
_SCOUT_AUDIT = _REPO / ".cache" / "platform" / "premium_scout.jsonl"

# Statuses eligible to emit paper/shadow intents (live still gated by autonomy_loop).
ELIGIBLE_STATUSES = frozenset({"testing", "paper", "shadow", "live"})
# Sleeves that produce premium-sale intents via pick_entry.
PREMIUM_SLEEVES = frozenset({"premium"})

RecProvider = Callable[[str], dict[str, Any]]


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def audit_scout(event: str, payload: dict[str, Any]) -> None:
    _SCOUT_AUDIT.parent.mkdir(parents=True, exist_ok=True)
    line = {"ts": _now(), "event": event, **payload}
    with _SCOUT_AUDIT.open("a") as f:
        f.write(json.dumps(line, default=str) + "\n")


@dataclass
class RegimeSnapshot:
    symbol: str
    regime: str
    iv_rank: float
    high_iv: bool
    reversal: bool
    spot: float
    date: str
    source: str = "live.make_recommendation"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ScoutCandidate:
    """One stage-4 outcome for (strategy, symbol)."""

    hypothesis_id: str
    hypothesis_name: str
    sleeve: str
    symbol: str
    regime: RegimeSnapshot
    action: str  # STAND_ASIDE | SELL_PUT | SELL_CALL | OPEN_PCS | OPEN_CCS | OPEN_IC | SKIP
    reason: str
    intent: Optional[OrderIntent] = None
    strike: Optional[float] = None
    expiration: Optional[str] = None
    dte: Optional[int] = None
    estimated_credit: Optional[float] = None
    stage_trace: list[str] = field(default_factory=list)
    # Multi-leg PCS extras (optional)
    structure: Optional[str] = None
    short_strike: Optional[float] = None
    long_strike: Optional[float] = None
    width: Optional[float] = None
    max_loss_usd: Optional[float] = None
    legs: Optional[list[dict[str, Any]]] = None

    def to_dict(self) -> dict[str, Any]:
        d = {
            "hypothesis_id": self.hypothesis_id,
            "hypothesis_name": self.hypothesis_name,
            "sleeve": self.sleeve,
            "symbol": self.symbol,
            "regime": self.regime.to_dict() if self.regime else None,
            "action": self.action,
            "reason": self.reason,
            "strike": self.strike,
            "expiration": str(self.expiration) if self.expiration is not None else None,
            "dte": self.dte,
            "estimated_credit": self.estimated_credit,
            "stage_trace": list(self.stage_trace),
            "structure": self.structure,
            "short_strike": self.short_strike,
            "long_strike": self.long_strike,
            "width": self.width,
            "max_loss_usd": self.max_loss_usd,
            "legs": self.legs,
        }
        if self.intent is not None:
            d["intent"] = {
                "symbol": self.intent.symbol,
                "side": self.intent.side,
                "qty": self.intent.qty,
                "order_type": self.intent.order_type,
                "limit_price": self.intent.limit_price,
                "strategy_id": self.intent.strategy_id,
                "tag": self.intent.tag,
                "notional": self.intent.estimated_notional(),
                "risk_amount": self.intent.risk_amount(),
                "structure": self.intent.structure,
                "max_loss_usd": self.intent.max_loss_usd,
                "width": self.intent.width,
                "net_credit": self.intent.net_credit,
                "short_strike": self.intent.short_strike,
                "long_strike": self.intent.long_strike,
                "legs": self.intent.legs,
                "expiration": self.intent.expiration,
                "dte": self.intent.dte,
            }
        return d


def default_rec_provider(ticker: str) -> dict[str, Any]:
    """Live short-premium recommendation (same path as just test / live.py)."""
    from live import make_recommendation

    return make_recommendation(ticker)


_OPEN_ACTIONS = frozenset({"OPEN_PCS", "OPEN_CCS", "OPEN_IC"})

_STRUCTURE_OPEN = {
    "put_credit_spread": ("OPEN_PCS", "pcs", "put"),
    "call_credit_spread": ("OPEN_CCS", "ccs", "call"),
    "iron_condor": ("OPEN_IC", "ic", "iron_condor"),
}


def _structure_open_meta(structure: str) -> tuple[str, str, str]:
    """(action, tag_slug, primary_right_label) for defined-risk DNA structure."""
    s = (structure or "put_credit_spread").strip().lower()
    return _STRUCTURE_OPEN.get(s, ("OPEN_PCS", "pcs", "put"))


def _legs_for_trade(trade: Any) -> list[dict[str, Any]]:
    """Build multi-leg open legs from a PcsTrade (PCS / CCS / IC)."""
    right = str(getattr(trade, "right", "put") or "put")
    if right == "iron_condor":
        return [
            {
                "action": "sell",
                "right": "put",
                "strike": float(trade.short_strike),
                "qty": 1,
                "position_effect": "open",
            },
            {
                "action": "buy",
                "right": "put",
                "strike": float(trade.long_strike),
                "qty": 1,
                "position_effect": "open",
            },
            {
                "action": "sell",
                "right": "call",
                "strike": float(trade.call_short_strike),
                "qty": 1,
                "position_effect": "open",
            },
            {
                "action": "buy",
                "right": "call",
                "strike": float(trade.call_long_strike),
                "qty": 1,
                "position_effect": "open",
            },
        ]
    leg_right = "call" if right == "call" else "put"
    return [
        {
            "action": "sell",
            "right": leg_right,
            "strike": float(trade.short_strike),
            "qty": 1,
            "position_effect": "open",
        },
        {
            "action": "buy",
            "right": leg_right,
            "strike": float(trade.long_strike),
            "qty": 1,
            "position_effect": "open",
        },
    ]


def make_pcs_recommendation(
    ticker: str,
    dna: Any,
    *,
    df: Any = None,
    sleeve_usd: float = 3000.0,
    open_risk_budget_usd: float = 750.0,
) -> dict[str, Any]:
    """Live-clock defined-risk multi-leg entry (paper path).

    Uses pcs_sim.pick_structure_entry for put_credit_spread / call_credit_spread /
    iron_condor. Returns OPEN_PCS | OPEN_CCS | OPEN_IC with legs + max_loss_usd,
    or STAND_ASIDE with an explicit reason.

    Name kept for call-site compatibility; structure comes from DNA (not PCS-only).
    """
    from data import build
    from trader_platform.research.pcs_sim import capital_fit_pcs, pick_structure_entry
    from trader_platform.strategy_dna import StrategyDNA

    if isinstance(dna, dict):
        dna = StrategyDNA.from_dict(dna)
    if dna is None:
        raise ValueError("make_pcs_recommendation requires StrategyDNA")

    t = ticker.upper()
    structure = str(dna.structure or "put_credit_spread")
    open_action, tag_slug, right_label = _structure_open_meta(structure)
    if df is None:
        df = build(t, period="2y")
    today_row = df.iloc[-1]
    today_date = df.index[-1]
    spot = float(today_row["close"])
    cfg = dna.pcs_config()

    features = {
        "iv_rank": float(today_row.get("iv_rank") or 0.0),
        "iv_proxy": float(today_row.get("iv_proxy") or 0.0),
        "ret_14d_pct": float(today_row.get("ret_14d") or 0.0) * 100,
        "rsi_14": float(today_row.get("rsi_14") or 0.0),
        "macd_hist": float(today_row.get("macd_hist") or 0.0),
        "volume_surge": float(today_row.get("volume_surge") or 0.0),
        "intraday_ret_pct": float(today_row.get("intraday_return") or 0.0),
        "regime": str(today_row.get("regime") or "unknown"),
        "reversal": bool(today_row.get("reversal")),
        "high_iv": bool(today_row.get("high_iv")),
    }
    base: dict[str, Any] = {
        "ticker": t,
        "date": today_date,
        "spot": spot,
        "features": features,
        "regime_at_entry": features["regime"],
        "dna_id": dna.ensure_id(),
        "dna_structure": structure,
        "structure": structure,
        "strategy_dna": {
            "dna_id": dna.ensure_id(),
            "structure": structure,
            "entry_plan": dna.entry_plan,
            "exit_plan": dna.exit_plan,
            "config": cfg,
        },
    }

    trade = pick_structure_entry(today_row, spot, today_date, cfg, structure=structure)
    if trade is None:
        base["action"] = "STAND_ASIDE"
        base["reason"] = _why_no_defined_risk(today_row, cfg, structure=structure)
        return base

    max_loss_usd = float(trade.max_loss_per_share) * 100.0
    budget = float(cfg.get("max_loss_budget_usd") or 300.0)
    cap = capital_fit_pcs(
        max_loss_usd=max_loss_usd,
        sleeve_usd=sleeve_usd,
        open_risk_budget_usd=open_risk_budget_usd,
        max_loss_budget_usd=budget,
    )
    if not cap.get("fits_open_risk_budget") or int(cap.get("max_lots") or 0) < 1:
        base["action"] = "STAND_ASIDE"
        base["reason"] = (
            f"{tag_slug.upper()} capital envelope fail: max_loss_usd≈${max_loss_usd:.0f} "
            f"fit={cap.get('capital_fit')} open_risk_budget={open_risk_budget_usd}"
        )
        base["max_loss_usd"] = round(max_loss_usd, 2)
        base["capital_fit"] = cap
        return base

    exp = trade.expiration
    exp_s = str(exp.date()) if hasattr(exp, "date") else str(exp)
    credit = float(trade.net_credit)
    legs = _legs_for_trade(trade)
    wing_note = ""
    if right_label == "iron_condor":
        wing_note = (
            f" put_wing Ks={trade.short_strike}/{trade.long_strike} "
            f"call_wing Ks={trade.call_short_strike}/{trade.call_long_strike}"
        )
    else:
        wing_note = f" short_{right_label} K={trade.short_strike} long_{right_label} K={trade.long_strike}"
    base.update(
        {
            "action": open_action,
            "reason": (
                f"{open_action} {t}{wing_note} "
                f"w={trade.width} dte={trade.dte_at_entry} credit≈${credit:.2f} "
                f"max_loss≈${max_loss_usd:.0f} regime={trade.regime_at_entry}"
            ),
            "strike": float(trade.short_strike),
            "short_strike": float(trade.short_strike),
            "long_strike": float(trade.long_strike),
            "width": float(trade.width),
            "expiration": exp_s,
            "dte": int(trade.dte_at_entry),
            "estimated_credit": credit,
            "net_credit": credit,
            "max_loss_usd": round(max_loss_usd, 2),
            "capital_fit": cap,
            "capital_fit_usd": cap.get("capital_fit_usd"),
            "max_lots": cap.get("max_lots"),
            "legs": legs,
            "iv_used": float(trade.iv_at_entry),
            "short_delta_entry": float(trade.short_delta_entry),
            "regime_at_entry": trade.regime_at_entry,
            "tag_slug": tag_slug,
        }
    )
    if right_label == "iron_condor":
        base["call_short_strike"] = float(trade.call_short_strike)
        base["call_long_strike"] = float(trade.call_long_strike)
        base["call_width"] = float(getattr(trade, "call_width", 0.0) or 0.0)
    return base


def _why_no_pcs(row: Any, cfg: dict[str, Any]) -> str:
    """Backward-compatible alias for put-credit stand-aside reasons."""
    return _why_no_defined_risk(row, cfg, structure="put_credit_spread")


def _why_no_defined_risk(
    row: Any, cfg: dict[str, Any], *, structure: str = "put_credit_spread"
) -> str:
    """Human reason when pick_structure_entry returns None."""
    label = _structure_open_meta(structure)[1].upper()
    try:
        iv = float(row.get("iv_proxy") or 0.0)
        if iv <= 0:
            return f"{label}: no valid IV"
        iv_rank_min = float(cfg.get("iv_rank_min") or 0.0)
        ivr = float(row.get("iv_rank") or 0.0)
        if ivr < iv_rank_min:
            return f"{label}: iv_rank {ivr:.1f} below floor {iv_rank_min}"
        regime = str(row.get("regime") or "")
        s = (structure or "").strip().lower()
        if (
            s == "put_credit_spread"
            and regime == "bearish"
            and int(cfg.get("bear_dte") or 0) <= 0
        ):
            return (
                f"{label}: bearish regime — stand aside "
                "(bear_dte=0; capital-fit put credit not probed)"
            )
        return (
            f"{label}: filters blocked entry (credit/width/max_loss_budget or strike construction) "
            f"— structure={s or 'put_credit_spread'} regime={regime} ivr={ivr:.1f}"
        )
    except Exception:  # noqa: BLE001
        return f"{label}: stand aside (entry filter)"


def rec_provider_for_hyp(hyp: Hypothesis) -> RecProvider:
    """If hypothesis carries Strategy DNA, use its entry/exit config for recs.

    Defined-risk multi-leg DNA (PCS/CCS/IC) uses pcs_sim paper path
    (OPEN_PCS | OPEN_CCS | OPEN_IC), never single-leg pick_entry
    (which would emit a false SELL_PUT / SELL_CALL).
    """
    dna_raw = getattr(hyp, "dna", None) or None
    if not dna_raw:
        return default_rec_provider
    try:
        from live import make_recommendation
        from strategies import get_config
        from trader_platform.strategy_dna import StrategyDNA

        dna = StrategyDNA.from_dict(dna_raw)
        if dna is None:
            return default_rec_provider

        if dna.uses_pcs_sim():

            def _pcs_prov(ticker: str) -> dict[str, Any]:
                return make_pcs_recommendation(ticker.upper(), dna)

            return _pcs_prov

        overrides = dna.config_overrides()

        def _prov(ticker: str) -> dict[str, Any]:
            cfg = get_config(ticker.upper(), **overrides)
            rec = dict(make_recommendation(ticker.upper(), cfg=cfg))
            rec["dna_id"] = dna.ensure_id()
            rec["dna_structure"] = dna.structure
            rec["strategy_dna"] = {
                "dna_id": dna.ensure_id(),
                "structure": dna.structure,
                "entry_plan": dna.entry_plan,
                "exit_plan": dna.exit_plan,
                "config": overrides,
            }
            return rec

        return _prov
    except Exception:  # noqa: BLE001 — fall back to default engine
        return default_rec_provider


def _regime_from_rec(symbol: str, rec: dict[str, Any]) -> RegimeSnapshot:
    feats = rec.get("features") or {}
    date = rec.get("date")
    return RegimeSnapshot(
        symbol=symbol.upper(),
        regime=str(feats.get("regime") or "unknown"),
        iv_rank=float(feats.get("iv_rank") or 0.0),
        high_iv=bool(feats.get("high_iv")),
        reversal=bool(feats.get("reversal")),
        spot=float(rec.get("spot") or 0.0),
        date=str(date) if date is not None else "",
    )


def select_strategies(
    registry: HypothesisRegistry,
    *,
    statuses: Iterable[str] = ELIGIBLE_STATUSES,
    sleeves: Iterable[str] = PREMIUM_SLEEVES,
) -> list[Hypothesis]:
    """Stage 2 — strategy selection from hypothesis registry."""
    status_set = set(statuses)
    sleeve_set = set(sleeves)
    registry.ensure_seeded()
    out: list[Hypothesis] = []
    for h in registry.list():
        if h.status not in status_set:
            continue
        if h.sleeve not in sleeve_set:
            continue
        if not h.instruments:
            continue
        # Prefer entry refs that map to pick_entry / short-premium; skip pure PMCC for v1 scout.
        ref = (h.entry_logic_ref or "").lower()
        if "pmcc" in ref and "pick_entry" not in ref:
            continue
        out.append(h)
    return out


def select_symbols(hyp: Hypothesis, *, only: Optional[Sequence[str]] = None) -> list[str]:
    """Stage 3 — symbols for a strategy."""
    symbols = [s.upper() for s in (hyp.instruments or [])]
    if only:
        allow = {s.upper() for s in only}
        symbols = [s for s in symbols if s in allow]
    return symbols


def _is_tradable_action(action: str) -> bool:
    a = (action or "").upper()
    return a.startswith("SELL_") or a in _OPEN_ACTIONS


def rec_to_intent(
    rec: dict[str, Any],
    *,
    hypothesis_id: str,
    qty: float = 1.0,
    event: str = "premium_scout",
) -> tuple[str, str, Optional[OrderIntent], dict[str, Any]]:
    """Map a live recommendation dict → (action, reason, intent|None, meta)."""
    action = str(rec.get("action") or "STAND_ASIDE")
    symbol = str(rec.get("ticker") or "").upper()
    meta: dict[str, Any] = {
        "strike": rec.get("strike"),
        "expiration": rec.get("expiration"),
        "dte": rec.get("dte"),
        "estimated_credit": rec.get("estimated_credit"),
        "regime_at_entry": rec.get("regime_at_entry")
        or (rec.get("features") or {}).get("regime"),
        "structure": rec.get("structure") or rec.get("dna_structure"),
        "short_strike": rec.get("short_strike"),
        "long_strike": rec.get("long_strike"),
        "width": rec.get("width"),
        "max_loss_usd": rec.get("max_loss_usd"),
        "legs": rec.get("legs"),
        "net_credit": rec.get("net_credit", rec.get("estimated_credit")),
        "capital_fit": rec.get("capital_fit"),
        "call_short_strike": rec.get("call_short_strike"),
        "call_long_strike": rec.get("call_long_strike"),
    }

    if action == "STAND_ASIDE":
        return action, str(rec.get("reason") or "stand_aside"), None, meta

    # --- Multi-leg defined-risk PCS / CCS / IC ---
    if action in _OPEN_ACTIONS:
        credit = rec.get("estimated_credit")
        max_loss = rec.get("max_loss_usd")
        legs = rec.get("legs")
        structure = str(
            rec.get("structure")
            or rec.get("dna_structure")
            or {
                "OPEN_PCS": "put_credit_spread",
                "OPEN_CCS": "call_credit_spread",
                "OPEN_IC": "iron_condor",
            }.get(action, "put_credit_spread")
        )
        tag_slug = str(rec.get("tag_slug") or _structure_open_meta(structure)[1])
        min_legs = 4 if action == "OPEN_IC" else 2
        if credit is None or float(credit) <= 0:
            return "SKIP", f"{tag_slug.upper()} missing or non-positive estimated_credit", None, meta
        if max_loss is None or float(max_loss) <= 0:
            return "SKIP", f"{tag_slug.upper()} missing max_loss_usd", None, meta
        if not legs or len(legs) < min_legs:
            return "SKIP", f"{tag_slug.upper()} missing multi-leg legs", None, meta
        limit_price = round(float(credit), 2)
        ml = round(float(max_loss), 2)
        width = rec.get("width")
        short_k = rec.get("short_strike")
        long_k = rec.get("long_strike")
        tag = (
            f"scout:{event}|{tag_slug}|w={width}|Ks={short_k}|Kl={long_k}"
            f"|dte={meta.get('dte')}|exp={meta.get('expiration')}|ml={ml}"
        )
        intent = OrderIntent(
            symbol=symbol,
            side="sell",
            qty=qty,
            order_type="limit",
            limit_price=limit_price,
            strategy_id=hypothesis_id,
            multiplier=100.0,
            tag=tag,
            structure=structure,
            defined_risk=True,
            legs=list(legs),
            max_loss_usd=ml,
            width=float(width) if width is not None else None,
            net_credit=float(credit),
            short_strike=float(short_k) if short_k is not None else None,
            long_strike=float(long_k) if long_k is not None else None,
            expiration=str(meta["expiration"]) if meta.get("expiration") is not None else None,
            dte=int(meta["dte"]) if meta.get("dte") is not None else None,
        )
        reason = str(
            rec.get("reason")
            or (
                f"{action} {symbol} Ks={short_k} Kl={long_k} "
                f"credit≈${limit_price:.2f} max_loss≈${ml:.0f}"
            )
        )
        return action, reason, intent, meta

    if not action.startswith("SELL_"):
        return "SKIP", f"unsupported action {action}", None, meta

    credit = rec.get("estimated_credit")
    if credit is None or float(credit) <= 0:
        return "SKIP", "missing or non-positive estimated_credit", None, meta

    limit_price = round(float(credit), 2)
    option_side = "put" if action == "SELL_PUT" else "call"
    tag = (
        f"scout:{event}|{option_side}|K={meta.get('strike')}|dte={meta.get('dte')}"
        f"|exp={meta.get('expiration')}"
    )
    intent = OrderIntent(
        symbol=symbol,
        side="sell",
        qty=qty,
        order_type="limit",
        limit_price=limit_price,
        strategy_id=hypothesis_id,
        multiplier=100.0,
        tag=tag,
        structure=str(meta.get("structure") or "single_leg"),
        short_strike=float(meta["strike"]) if meta.get("strike") is not None else None,
        expiration=str(meta["expiration"]) if meta.get("expiration") is not None else None,
        dte=int(meta["dte"]) if meta.get("dte") is not None else None,
        net_credit=float(credit),
    )
    reason = (
        f"{action} {symbol} K={meta.get('strike')} "
        f"dte={meta.get('dte')} credit≈${limit_price:.2f} "
        f"regime={meta.get('regime_at_entry')}"
    )
    return action, reason, intent, meta


def scout_symbol(
    hyp: Hypothesis,
    symbol: str,
    *,
    rec_provider: Optional[RecProvider] = None,
    qty: float = 1.0,
    event: str = "premium_scout",
) -> ScoutCandidate:
    """Stages 1+4 for one (hypothesis, symbol). Uses hyp DNA when present."""
    provider = rec_provider or rec_provider_for_hyp(hyp)
    trace = [
        f"strategy:{hyp.id}:{hyp.sleeve}:{hyp.status}",
        f"symbol:{symbol.upper()}",
    ]
    if getattr(hyp, "dna", None):
        d = hyp.dna or {}
        trace.append(f"dna:{d.get('structure')}:{d.get('dna_id')}")
    try:
        rec = provider(symbol.upper())
    except Exception as exc:  # noqa: BLE001 — scout must not crash the tick
        audit_scout(
            "scout_error",
            {"hypothesis_id": hyp.id, "symbol": symbol, "error": str(exc)},
        )
        empty_regime = RegimeSnapshot(
            symbol=symbol.upper(),
            regime="error",
            iv_rank=0.0,
            high_iv=False,
            reversal=False,
            spot=0.0,
            date="",
            source="error",
        )
        return ScoutCandidate(
            hypothesis_id=hyp.id,
            hypothesis_name=hyp.name,
            sleeve=hyp.sleeve,
            symbol=symbol.upper(),
            regime=empty_regime,
            action="SKIP",
            reason=f"rec_provider error: {exc}",
            stage_trace=trace + [f"error:{exc}"],
        )

    regime = _regime_from_rec(symbol, rec)
    trace.append(f"regime:{regime.regime}:ivr={regime.iv_rank:.1f}")
    action, reason, intent, meta = rec_to_intent(
        rec, hypothesis_id=hyp.id, qty=qty, event=event
    )
    trace.append(f"premium:{action}")
    return ScoutCandidate(
        hypothesis_id=hyp.id,
        hypothesis_name=hyp.name,
        sleeve=hyp.sleeve,
        symbol=symbol.upper(),
        regime=regime,
        action=action,
        reason=reason,
        intent=intent,
        strike=meta.get("strike"),
        expiration=str(meta["expiration"]) if meta.get("expiration") is not None else None,
        dte=int(meta["dte"]) if meta.get("dte") is not None else None,
        estimated_credit=float(meta["estimated_credit"])
        if meta.get("estimated_credit") is not None
        else None,
        stage_trace=trace,
        structure=str(meta["structure"]) if meta.get("structure") is not None else None,
        short_strike=float(meta["short_strike"]) if meta.get("short_strike") is not None else None,
        long_strike=float(meta["long_strike"]) if meta.get("long_strike") is not None else None,
        width=float(meta["width"]) if meta.get("width") is not None else None,
        max_loss_usd=float(meta["max_loss_usd"]) if meta.get("max_loss_usd") is not None else None,
        legs=list(meta["legs"]) if meta.get("legs") else None,
    )


@dataclass
class ScoutReport:
    event: str
    candidates: list[ScoutCandidate]
    intents: list[OrderIntent]
    stand_asides: list[ScoutCandidate]
    skipped: list[ScoutCandidate]
    audit_path: str = str(_SCOUT_AUDIT)

    def to_dict(self) -> dict[str, Any]:
        return {
            "event": self.event,
            "n_candidates": len(self.candidates),
            "n_intents": len(self.intents),
            "n_stand_asides": len(self.stand_asides),
            "n_skipped": len(self.skipped),
            "candidates": [c.to_dict() for c in self.candidates],
            "audit_path": self.audit_path,
        }


def run_premium_scout(
    *,
    registry: Optional[HypothesisRegistry] = None,
    symbols: Optional[Sequence[str]] = None,
    rec_provider: Optional[RecProvider] = None,
    qty: float = 1.0,
    event: str = "premium_scout",
    max_intents: int = 3,
    audit: bool = True,
) -> ScoutReport:
    """Full pipeline: regime → strategy → symbol → premium → intent list.

    max_intents caps paper proposals per tick (risk + ops hygiene).
    When rec_provider is None, each hypothesis uses its own DNA-aware provider.
    """
    reg = registry or HypothesisRegistry()
    strategies = select_strategies(reg)
    candidates: list[ScoutCandidate] = []

    for hyp in strategies:
        for sym in select_symbols(hyp, only=symbols):
            cand = scout_symbol(
                hyp, sym, rec_provider=rec_provider, qty=qty, event=event
            )
            candidates.append(cand)

    intents: list[OrderIntent] = []
    stand_asides: list[ScoutCandidate] = []
    skipped: list[ScoutCandidate] = []
    # Prefer any defined-risk multi-leg OPEN_* over naked single-leg when capping
    # intents. This is ops hygiene (bounded risk first), not strategy rank order —
    # Ken pin 2026-07-10: evidence ranks DNA; plumbing must not demote peers.
    ranked = sorted(
        candidates,
        key=lambda c: (
            0 if (c.action in _OPEN_ACTIONS and c.intent is not None) else 1,
            0 if (c.max_loss_usd is not None) else 1,
        ),
    )
    selected_ids: set[int] = set()
    for c in ranked:
        if c.intent is not None and _is_tradable_action(c.action):
            if len(intents) < max_intents:
                intents.append(c.intent)
                selected_ids.add(id(c))
            else:
                c.action = "SKIP"
                c.reason = f"max_intents={max_intents} reached; {c.reason}"
                c.intent = None
                skipped.append(c)
                continue
        elif c.action == "STAND_ASIDE":
            stand_asides.append(c)
        else:
            if id(c) not in selected_ids and c not in skipped and c not in stand_asides:
                skipped.append(c)

    report = ScoutReport(
        event=event,
        candidates=candidates,
        intents=intents,
        stand_asides=stand_asides,
        skipped=skipped,
    )
    if audit:
        audit_scout(
            "scout_complete",
            {
                "event": event,
                "n_candidates": len(candidates),
                "n_intents": len(intents),
                "n_stand_asides": len(stand_asides),
                "n_skipped": len(skipped),
                "strategies": [h.id for h in strategies],
                "actions": [c.action for c in candidates],
            },
        )
    return report



def main(argv: Optional[list[str]] = None) -> int:
    import argparse

    p = argparse.ArgumentParser(
        description="Premium scout: regime→strategy→symbol→premium (paper-first intents)"
    )
    p.add_argument("--event", default="manual_scout")
    p.add_argument("--symbols", nargs="*", default=None, help="Limit to these underlyings")
    p.add_argument("--qty", type=float, default=1.0)
    p.add_argument("--max-intents", type=int, default=3)
    p.add_argument("--json", action="store_true")
    p.add_argument(
        "--stub",
        action="store_true",
        help="Use offline stub recs (no network / no live.py) for CI smoke",
    )
    args = p.parse_args(argv)

    if args.stub:
        def _stub(ticker: str) -> dict[str, Any]:
            # Deterministic offline rec for smoke: TSLA sell put, TSLL stand aside.
            t = ticker.upper()
            if t == "TSLA":
                return {
                    "ticker": "TSLA",
                    "date": "2026-07-09",
                    "spot": 250.0,
                    "action": "SELL_PUT",
                    "strike": 230.0,
                    "expiration": "2026-07-25",
                    "dte": 16,
                    "estimated_credit": 1.85,
                    "features": {
                        "regime": "bullish",
                        "iv_rank": 55.0,
                        "high_iv": False,
                        "reversal": False,
                    },
                    "regime_at_entry": "bullish",
                }
            return {
                "ticker": t,
                "date": "2026-07-09",
                "spot": 20.0,
                "action": "STAND_ASIDE",
                "reason": "stub: iv_rank below floor",
                "features": {
                    "regime": "neutral",
                    "iv_rank": 10.0,
                    "high_iv": False,
                    "reversal": False,
                },
            }

        report = run_premium_scout(
            symbols=args.symbols,
            rec_provider=_stub,
            qty=args.qty,
            event=args.event,
            max_intents=args.max_intents,
        )
    else:
        report = run_premium_scout(
            symbols=args.symbols,
            qty=args.qty,
            event=args.event,
            max_intents=args.max_intents,
        )

    if args.json:
        print(json.dumps(report.to_dict(), indent=2, default=str))
    else:
        print(
            f"scout event={report.event} candidates={len(report.candidates)} "
            f"intents={len(report.intents)} stand_asides={len(report.stand_asides)} "
            f"skipped={len(report.skipped)}"
        )
        for c in report.candidates:
            print(
                f"  [{c.action}] {c.symbol} hyp={c.hypothesis_id} "
                f"regime={c.regime.regime} — {c.reason}"
            )
            if c.stage_trace:
                print(f"    trace: {' → '.join(c.stage_trace)}")
        print(f"audit: {report.audit_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
