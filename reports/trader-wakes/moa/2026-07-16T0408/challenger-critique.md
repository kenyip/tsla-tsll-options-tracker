# Challenger critique — 2026-07-16T0408 (Grok 4.5)

Phase: BUILD / L0 discovery
Role: read-only judgment; no evolve --apply; no broker; no arm; no commit/push/merge
Verdict: **PASS WITH NITS**
Accepted strategy outcome: **`FAMILY_CLOSED`** at **F0** for
`CREDIT_RISK_OFF_SPY_BEAR_PUT_21D_V1` / `HIGH_YIELD_CREDIT_DIVERGENCE_FORWARD_DOWNSIDE`
Strategy advancement: **false** (factory + ULP repair = search information only)
Authority: L0 underlying discovery only; no F1/F2/L1, living candidate, capital seat, paper, shadow, arm, or live

## Independent verification (read-only)

Claim artifact: the run-local canonical factory claim JSON

| Check | Result |
|---|---|
| Raw SHA-256 | `3127839938f7cb25b2612c2f591bbba379ddffb7d3c89bfc3f0aa17962844377` matches executor |
| `strategy_outcome` | `FAMILY_CLOSED`; `strategy_advancement=false`; `factory_is_strategy_progress=false`; `claim_bar=L0_DISCOVERY_ONLY` |
| Panel | SPY/HYG/IEF exact-date join **4,832** rows, 2007-05-01..2026-07-15; hash-cited CSVs; no forward fill |
| Primary train | eligible/matched **42/41**; support **97.6190%**; **10** signal years; integrity_violations=[] |
| Primary means (recomputed from 41 pairs) | signed event **−0.909825%**; control **−0.201659%**; paired excess **−0.708167%** — exact match |
| Primary hit / tail | event-signed pos **29.2683%**; worst-decile **−4.015427%** (n=5) — exact match |
| Primary LB90 | claim **−1.360006%** (circular 3-pair block, 10k samples) — machine field present |
| Primary failed gates (4) | signed event mean; paired excess mean; paired LB90; signed pos frequency ≥55% |
| Primary passed gates | n≥36; years≥8; support≥80%; worst-decile ≥−5%; zero integrity |
| Holdout seal (primary) | n_matched **28**; `outcome_metrics_read=false`; `simulation_run=false`; option_pricing_calls **0**; SHA `83fc5c0fe69de6801d440970c53edc8c098d09bd3edf0cdbe7728a41707c1c23` |
| Chronology / controls | control_exit before signal for all 41; control reuse 0; episode entry/exit overlaps 0; next-close entry samples consistent |
| Secondary (search info only) | n32/34; support 94.12%; event **+0.511192%**; paired **+0.739330%**; hit **71.875%**; LB90 **−0.200722%**; fails `minimum_train_pairs` + LB90; holdout 24 unread SHA `40113d83…`; pricing 0 |
| Focused tests | `tests/test_train_only_defined_risk_candidate_factory.py` → **6 passed** (challenger re-ran) |
| Capital planning | both stacks `capital_fit_usd=200`, planning `max_loss_usd=200`, `max_lots=1`; no seat |

Economic judgment: the primary signed forecast is **wrong** in train. After the exact HYG−IEF risk-off trigger inside an SPY uptrend envelope, SPY five-session signed outcomes are negative and worse than prior same-regime non-trigger controls. A future bear-put debit wrapper would monetize the inverse of the measured edge and cannot salvage F0.

Secondary overnight/intraday disagreement has favorable centers but fails frozen density (n32&lt;36) and dependence-aware uncertainty (LB90≤0). It is **not** F1, **not** a second claim-bearing close, and **not** a retune invitation.

## Rubric

1. **Strategy charter** — **PASS**. Predeclared factory rules, two complete Layered Edge Stacks, F0→F1-or-primary-close decision rule, frozen multi-gate falsifier, and exactly one claim-bearing outcome (`FAMILY_CLOSED` on credit-risk primary). Secondary explicitly non-claim-bearing.
2. **Strategy vs operations** — **PASS**. Factory tooling and 1-ULP adjusted-OHLCV validator repair are labeled search information / evidence integrity, not strategy advancement. Experiment was exercised to a closeout in-wake.
3. **Goal progress** — **PASS**. Honest discriminating F0 falsification of a free cross-asset credit-leading mechanism improves the closed-family map; sealed holdouts preserve optionality without peeking; no false paper/L1 claim.
4. **Creativity and independence** — **PASS**. Materially different from sector-leader, FOMC/Beige Book, residual/breadth/breakout, and TSLA/TSLL/PCS tunnels. Prior factory NEXT treated as justified context (orientation: zero living candidates; executable underlying route; no pivot/stop yet) and executed to a real decision, not scaffolding theater.
5. **Claim validity** — **PASS WITH NIT**. Prerequisites match the experiment (adjusted daily SPY/HYG/IEF only). ETF composition/survivorship and non-point-in-time credit-spread limits are stated. No option marks / L1 / seat. **Nit:** machine `dominant_failure_mechanism` text lists density/support/tail as possible failures even though those gates **passed** for the primary; human closeout is correct — finalizer should tighten the machine string to the four actual failed gates / wrong-sign anti-edge.
6. **Evidence and test quality** — **PASS WITH NIT**. Real factory + focused behavioral/boundary/positive/negative-control tests (challenger 6/6). Full-suite counts (unittest 415; pytest 425+18) are executor-reported; finalizer must reconfirm. **Nits:** (a) executor prose “4,833 sessions” vs claim/provenance **4,832** rows — normalize to 4,832; (b) control match distances are long (primary max 680 / median 153 sessions; secondary max 723 / median 165) — persist as diagnostics, not salvage; (c) stamp still lacks schema-v2 `compounding.json` until finalizer.
7. **Falsification** — **PASS**. Predeclared gates; four clear primary failures; dominant failure = wrong signed direction + negative specificity; exact geometry + nearby threshold/option-wrapper salvage quarantined; reopen only with new credit construction / horizon / PIT credit-spread class / independent evidence.
8. **Capital honesty** — **PASS**. Zero living leader/seat; planning $200 width bound only; readiness remains BUILD / NOT READY; former TSLL PCS reference stays non-leader context.
9. **Research freedom** — **PASS**. Observed-option archive sparsity did not freeze independent underlying discovery; dual free mechanisms chosen without allowlist tunnel.
10. **ONE NEXT seed** — **PASS WITH NIT**. After acceptance this is the **second consecutive epoch no-advance** → next wake **must pivot** mechanism/evidence class. Executor `SEC_FORM4_CLUSTERED_INSIDER_BUYING_DIRECTION_F0` is a valid pivot **if** the next wake freezes a complete stack + fail-closed PIT rules and **exercises train advance-or-close in the same wake**. Do not retune credit/overnight thresholds, open sealed holdouts, or spend a wake only on EDGAR plumbing without a claim-bearing decision.

## Findings for finalizer

### Accept as-is
- Exact `FAMILY_CLOSED` at F0 for credit-risk primary; strategy advancement false.
- Secondary overnight screen remains search information only (no F1, no second family-close claim, no holdout open, no retune).
- Holdouts unread; option pricing zero; no registry / capital seat / paper / shadow / arm / live.
- Quarantine of exact credit geometry + nearby salvage on the same panel.
- Readiness living candidates = 0; quality leader = none.
- ULP/`np.isclose(rtol=atol=1e-12)` validator repair in shared adjusted-OHLCV path is a valid evidence-integrity fix (diff observed on `scripts/fomc_information_resolution_train_lab.py`); keep material geometry fail-closed.

### Nits (repair / harden; not outcome-invalidating)
1. **Missing `compounding.json` schema_version=2** for stamp `2026-07-16T0408` with outcome `FAMILY_CLOSED`, dual closed-family IDs, novelty keys, useful deltas (capability + falsification + stop rule), and no-advance counters. Finalizer must write before integration.
2. **Epoch / streak surfaces**: orientation entered with `consecutive_no_strategy_advance=1`, pivot/burst false. After accept+integrate, set **consecutive_no=2** and **`strategy_pivot_required=true`** (burst still false). Reconcile readiness prose that claims an active epoch “began at 0335” with `configs/search_epoch.json` still showing completed FOMC `2026-07-16T0112` — either register a durable successor-epoch record or stop implying a formal started_stamp that machine config does not carry.
3. **Panel count prose**: normalize 4,833 → **4,832** everywhere living (closeout already has correct claim JSON).
4. **Tighten machine dominant-failure string** to actual failed gates + wrong-sign/specificity anti-edge (not a generic density/support/tail laundry list).
5. **Match-quality diagnostics**: persist max/median control distance and extreme long-lookback note on readiness/compounding; do not widen match tolerances post hoc.
6. **Outcome taxonomy optional clarity**: ULP repair + unchanged retest could also be labeled `BLOCKER_REMOVED_AND_RETESTED` with `retest_decision=FAMILY_CLOSED`. Accepting pure `FAMILY_CLOSED` is fine if compounding records the repair as a useful delta, not strategy progress.
7. **Reconfirm verification** before postflight: focused factory tests + shared OHLCV/FOMC regressions + full suite; do not trust executor full counts alone.
8. **Foreign/unintended residue review**: ensure only intended factory/tests/claim/report/readiness paths ship; the FOMC OHLCV validator change is intentional shared plumbing — keep it, with tests covering ULP accept + material reject.
9. **Form 4 NEXT anti-theater**: next wake must not end as capability-only EDGAR scaffolding. Predeclare panel, Form 4 code/ownership/cluster/PIT timestamp rules, controls, signed horizon, defined-risk call-debit stack, and train gates **before outcomes**; close one named F0→F1 or FAMILY_CLOSED; fail closed on amendments/derivatives/late filings/issuer map/density.

### Rejected claims (none present)
No shadow/live/arm, no L1, no quality-leader resurrection, no holdout peek, no option-edge claim, no secondary F1 salvage, no overnight retune seed.

## Capital / readiness
- Sleeve $3k; no capital seat; no living candidate.
- B0–B8: BUILD / NOT READY; challenger does not promote any B-check beyond acknowledging BUILD-path B1/B5 evidence residue pending finalizer integration.
- Readiness NEXT already points at Form 4 pivot — **not wrong**; leave text, harden only via compounding/orientation counters and anti-theater discipline above.

## Hard stops observed
No live orders, broker login, evolve --apply by challenger, secrets commit, shadow/live auto-promotion, or main-account trading. Challenger writes critique residue only; no RUN COMPLETE.

## Disposition summary
| Item | Disposition |
|---|---|
| `FAMILY_CLOSED` F0 (credit primary) | **ACCEPT** |
| Strategy advancement false | **ACCEPT** |
| Secondary overnight as search info only | **ACCEPT** |
| Quarantine + reopen conditions | **ACCEPT** |
| ULP validator repair + retest | **ACCEPT** (search/integrity delta) |
| Form 4 pivot NEXT | **ACCEPT WITH DISCIPLINE NIT** |
| Missing compounding v2 + epoch streak=2/pivot | **FINALIZER REPAIR** |
| 4833 vs 4832 prose; generic dominant-failure string | **FINALIZER REPAIR** |
