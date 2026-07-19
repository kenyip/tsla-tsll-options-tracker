# Trader North Star — Principles & Living Alignment

**Status:** Living document — system alignment source of truth for Desk B (Agentic) and research.  
**Pinned:** 2026-07-19  
**Owner:** Ken (intent) · Trader/Jarvis (maintain + implement)  
**Audience:** humans, agents, and future self-learning loops.

When code, crons, or research plans conflict with this file, **update them to match this**, or amend this file with an explicit changelog entry. Do not silently re-introduce cartesian knob thrash as the primary edge path.

Related (do not replace):

| Doc | Role |
|---|---|
| [TRADER_LAYERED_EDGE_DOCTRINE.md](TRADER_LAYERED_EDGE_DOCTRINE.md) | Forecast → expression → management layers |
| [TRADER_SPINE_ARCHITECTURE.md](TRADER_SPINE_ARCHITECTURE.md) | Current implementable spine (StrategySpec → evaluate_proxy → living) |
| [TRADER_DUAL_DESK.md](TRADER_DUAL_DESK.md) | Desk A personal vs Desk B agentic |
| [DISCOVERY_AND_PAPER_FASTTRACK.md](DISCOVERY_AND_PAPER_FASTTRACK.md) | Operational discovery / paper path |
| [PROMOTION_GATES.md](PROMOTION_GATES.md) | What may advance toward live |

---

## 1. Why we build this

**Goal:** Find and run a durable **advantage / edge** on a small, defined-risk sleeve (~$3k Agentic), not maximize backtest vanity.

**Edge means:** In a stated **regime**, a named **thesis** produces **opportunities** that, after realistic costs and time discipline, have acceptable expectancy and tails — and the same rules still fire in paper/live without silent “zero trade” holdouts.

Success is:

1. At least one **thesis-level** edge that survives dual-cost chronological proof.  
2. Paper path proves plumbing (not the edge itself).  
3. Live only when Ken arms — never auto-live from research.

Stand-aside is a **valid win**. No trade is often the correct output of the system.

---

## 2. North-star pipeline (build toward this)

Invert “grid of knobs first.” The product orientation is:

```text
Market data
  → SIGNALS          (named, timestamped observables)
  → OPPORTUNITY      (who / when / why — or stand_aside)
  → STRUCTURE        (option type, exp, strikes, entry premium rule)
  → MANAGEMENT       (close premium / time / risk / thesis stops)
  → PROVE            (programmatic sim: train → holdout, costs, gates)
  → EXECUTE          (RiskGovernor → paper → Ken-armed live)
  → LEARN            (score by thesis × regime; extend catalog; densify winners only)
```

| Layer | Program | Human / LLM |
|---|---|---|
| Compute signals | ✅ primary | critique / propose new features |
| Detect opportunity templates | ✅ rules + small models | invent new templates |
| Invent thesis / mechanism | weak alone | ✅ sparse, deliberate |
| Map thesis → structure+manage DNA | library + defaults | first draft |
| Cartesian 10⁵ knob search | ❌ not primary | ❌ worse |
| Dual-cost proof & ranking | ✅ only | ❌ |
| Order path | ✅ only | **forbidden** |

**LLM smarts** are for hypothesis generation and narrative audit — **not** for placing orders or replacing the prove spine.

---

## 3. Core objects (canonical vocabulary)

Use these names in code, configs, and agent prompts.

### 3.1 Signal

Observable, timestamped feature. Not a vibe.

```text
Signal {
  id, asof, symbol?,
  value, unit?,
  source,          // e.g. bars, chain, portfolio, calendar
  quality          // ok | stale | missing
}
```

### 3.2 Opportunity

Claim that the market state is interesting **before** structure is chosen.

```text
Opportunity {
  asof, symbol,
  thesis_id,
  regime_tag,
  direction_bias,  // short_vol | long_vol | long_delta | flat | stand_aside
  urgency,         // now | wait | stand_aside
  confidence,
  evidence[],      // signal ids + values that fired
  constraints      // max_loss, no_earnings, dte_band, …
}
```

**No opportunity → no structure search.**

### 3.3 StructurePlan

How to express the opportunity with options.

```text
StructurePlan {
  structure,           // PCS | CCS | IC | debit vertical | …
  expiration_rule,     // target DTE band or calendar rule
  short_strike_rule,   // delta / %OTM / expected-move multiple
  long_strike_rule,    // width $ or wing rule
  entry_premium_rule,  // min credit % width, min $, or model target
  max_loss_usd,
  qty_rule             // default 1-lot until proven
}
```

### 3.4 ManagementPlan

Paired with entry — **one DNA**. Do not mix unrelated exits across entries.

```text
ManagementPlan {
  profit_take,     // % of credit, $ target, or premium/day rule (see §5)
  time_stop,       // dte_stop
  risk_stop,       // delta breach / 2× credit / defined-loss frac
  thesis_stop,     // regime flip → exit
  roll_rules,      // usually off on $3k sleeve
  do_nothing_ok    // hold-to-expiry only if intentional
}
```

### 3.5 Thesis

Named economic mechanism with frozen defaults.

```text
Thesis {
  thesis_id,
  economic_mechanism,   // plain English
  opportunity_rules,    // which signals → Opportunity
  structure_defaults,
  management_defaults,
  prove_gates,          // min trades, max loss, costs, …
  score_dimensions      // which metrics define “good” for this thesis
}
```

Today’s closest implementable freeze is `StrategySpec` JSON; the north star is to **re-express specs as theses** with explicit opportunity rules, not only management knobs.

### 3.6 EvaluationReport → Living seat

Prove output. Living seats are **research claims**, not live authority.

Prefer identity:

```text
thesis_id + symbol + coarse DNA hash
```

over thousands of near-duplicate mutant suffixes.

---

## 4. Signal catalog (starting inventory)

This catalog is **extensible**. Adding a signal = name it here (or in `configs/signal_catalog.yaml` when that file exists) + implement a pure feature function. Self-learning may **propose** signals; promotion into the catalog is a deliberate step.

### 4.1 Underlying / path

| Signal family | Examples |
|---|---|
| Price / trend | spot, ret_1d/5d/20d, EMA slope, HH/HL |
| Realized vol | HV10/20/60, vol-of-vol |
| Path stress | gap %, drawdown from peak, range compress/expand |
| Cross-asset | beta/corr to SPY/QQQ |

### 4.2 Options / premium (proxy today; chain later)

| Signal family | Examples |
|---|---|
| IV | IV, IV rank, IV percentile |
| Surface | term structure, put/call skew |
| Liquidity | bid-ask, OI, volume (live path) |
| Move | expected move vs realized |

### 4.3 Regime / event

| Signal family | Examples |
|---|---|
| Regime | bull / neutral / bear / unknown classifier |
| Event | earnings, FOMC, ex-div → stand_aside bias |
| Macro vol | VIX level / Δ |

### 4.4 Portfolio / constraint (always on)

| Signal family | Examples |
|---|---|
| Capital | open risk, sleeve left, max_loss budget |
| Occupancy | open lots, correlation to open names |
| Safety | kill switch, day PnL, mode (paper/live) |

### 4.5 Meta / learning

| Signal family | Examples |
|---|---|
| Thesis health | recent hit rate of thesis × regime |
| Setup quality | premium richness vs historical for same geometry |
| Staleness | days since last similar setup |

---

## 5. Evaluation dimensions (extensible scoreboard)

**Pass/fail gates** and **ranking scores** are separate and both must stay pluggable.

### 5.1 Principle

```text
gates  = hard constraints (must not violate sleeve / integrity / min sample)
scores = soft ranking among things that passed gates
```

New ideas (human or self-learning) enter as:

1. **Proposal** — name, definition, hypothesis (“why this is edge”).  
2. **Spec** — formula, units, higher/lower better, where computed (trade / day / opportunity).  
3. **Wire** — implement in prove spine or post-processor.  
4. **Gate or score** — explicit choice (never silent).  
5. **Changelog** — entry in §9.

### 5.2 Current primary dimensions (implemented / spine)

| Dimension | Role today |
|---|---|
| Dual-cost PnL (`slip_5pct`, `fixed_0p01`) | Gate + rank (worst axis) |
| n_trades | Gate (min sample) |
| max_loss_usd | Gate (capital fit) |
| max_dd | Gate + secondary rank |
| integrity | Gate |
| control beat (optional) | Gate on train when enabled |

### 5.3 Candidate dimensions (hypotheses — not yet required gates)

These are first-class **candidates** the system should be able to adopt without redesign.

| Dimension | Hypothesis | Status |
|---|---|---|
| **Premium capture / day** (or **PnL / day held**) | Prefer trades that earn efficiently per unit time; penalize capital stuck for little theta | **Hypothesis — prove** |
| **Credit % of width at entry** | Richer relative premium → better short-vol setups | Partial (entry filter) |
| **PnL / max_loss** (R-multiple) | Normalize edge by risk unit | Candidate |
| **Time-to-50%-credit** | Faster winners free sleeve | Candidate |
| **Stand-aside purity** | Correct non-trades matter | Partial in router metrics |
| **Regime-conditional expectancy** | Edge only in regime R | Candidate (thesis × regime scoreboard) |
| **Fill friction residual** | Proxy − paper/live mark gap | Later (L1) |

#### Worked example: premium / day (Ken hypothesis)

**Definition (draft — refine when implementing):**

```text
premium_per_day = (entry_credit - exit_debit) / max(days_in_trade, 1)
# or for open marks:
mark_capture_per_day = (entry_credit - current_debit) / max(days_held, 1)
```

**Possible uses:**

| Mode | Use |
|---|---|
| Score | Rank F2 seats by median premium/day on holdout (after costs) |
| Manage | Exit if premium/day falls below threshold *and* thesis weak |
| Gate | Optional min median premium/day after enough trades |

**Proof path:** implement as report field → add to scoreboard → compare vs pure $ PnL rank on same holdout → keep only if it improves out-of-sample or paper behavior.

Self-learning may propose thresholds; **promotion to gate** requires dual-cost holdout evidence and a changelog entry.

---

## 6. Learning system (how the document stays alive)

### 6.1 What may auto-adapt

| Allowed | How |
|---|---|
| Local densify of **proven** thesis DNA | ±1 step knobs after F1/F2 |
| Thesis × regime scoreboard weights | Within declared score dimensions |
| Opportunity confidence calibration | From closed-trade feedback |
| Symbol tier promote/demote | Evidence of F2 barrenness / capital fit |

### 6.2 What must not auto-mutate

| Forbidden without Ken / explicit promote | Why |
|---|---|
| Live arming | Authority firewall |
| Silent gate loosening (e.g. min_trades → 1) | False edge |
| Cartesian bag expansion as “progress” | We already paid that tax |
| LLM-written orders | Non-reproducible risk |

### 6.3 Self-learning proposal loop

```text
observe scoreboard / paper residuals
  → propose: new signal | new dimension | thesis kill | thesis variant
  → write Proposal stub (id, hypothesis, metric definition)
  → program proves on sealed holdout
  → if pass: open PR / changelog to catalog + optional gate/score wire
  → if fail: quarantine proposal id
```

Agents must treat **this file + proposal log** as the alignment surface, not ad-hoc labs.

---

## 7. Alignment checklist (for any change)

Before merging research or agent work, answer:

1. **Which layer?** Signal / Opportunity / Structure / Manage / Prove / Execute / Learn  
2. **Which thesis_id** (or “catalog only”)?  
3. **New parameter?** Is it inside a thesis default, or re-opening a cartesian grid?  
4. **New score/gate?** Named in §5 with definition and status  
5. **Authority?** Still research/paper unless Ken-armed  
6. **Dedup?** Prefer thesis-level seats over clone flood  
7. **Stand-aside?** Still a first-class success outcome  

If a change cannot answer (1)–(4), it is not aligned yet.

---

## 8. Migration from current spine (honest path)

We do **not** throw away working pieces. We re-aim them.

| Keep | Re-aim |
|---|---|
| `StrategySpec` + `evaluate_proxy` dual-cost train/holdout | Identity as thesis DNA; add score dimensions |
| Living registry | Dedupe; thesis × symbol keys |
| RiskGovernor + paper handoff | Unchanged authority model |
| Wave A coarse proof + densify winners | Correct search policy; not full 318k product |
| Discovery universe tiers | Symbol choice under Opportunity, not forever-on cartesian |

| Deprioritize as primary edge engine | |
|---|---|
| Dense discovery_grid product as todo list | |
| Ranking 800 near-identical F2s as “many edges” | |
| LLM densify / MoA as main progress | |

**Near-term implementation order (alignment backlog):**

1. Publish this north star (this doc).  
2. `configs/signal_catalog.yaml` skeleton + map existing features.  
3. Rephrase 1–2 seeds as thesis files with opportunity rules.  
4. Opportunity emitter (even rule-based) → structure builder → existing prove.  
5. Scoreboard columns pluggable — include **premium/day** as experimental score.  
6. Paper shortlist from deduped thesis winners.

---

## 9. Changelog (living)

| Date | Change |
|---|---|
| 2026-07-19 | Initial north star: signals→opportunity→structure→manage→prove→execute→learn; extensible evaluation dimensions; premium/day as candidate hypothesis; anti-cartesian-search pin |

---

## 10. One-paragraph summary (for agents)

Build toward a system that turns **named market signals** into **opportunities** (or stand-aside), expresses them with **frozen structure+management DNA**, **proves** them programmatically under dual costs and chronological holdout, **executes** only through RiskGovernor/paper/Ken-arm, and **learns** by scoring **theses × regimes** on an **extensible metric catalog** (gates vs scores). Do not equate knob-grid volume with edge. New ideas—including premium-per-day style efficiency metrics—enter as cataloged dimensions, get proven, then may become scores or gates. LLMs propose; programs measure and trade.
