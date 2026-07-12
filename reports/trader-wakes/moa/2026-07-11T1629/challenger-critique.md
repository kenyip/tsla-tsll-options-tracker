# MOA BUILD lab challenger critique — 2026-07-11T1629 (evening)

WAKE: 2026-07-11T1629
PHASE: BUILD
SLEEVE: 3000
CHALLENGER: grok-4.5 (xai-oauth) · read-only
EXECUTOR: gpt-5.6-sol (openai-codex)

## Verdict

**PASS 8/8** on the income-lab rubric. Executor closed a real catalog gap (credit `iron_butterfly`), ran multi-name research + one applied pop + exact B3/B4, rejected both candidates on non-vacuous cost fragility and ml/dd, kept L0 / `l1_hyp_ids=[]`, and left one concrete NEXT. No live/shadow/agentic claim.

## Rubric

| # | Check | Result | One line |
|---|---|---|---|
| 1 | Income goal honesty | **PASS** | $3k defined-risk framing; no vanity $ promote; leader itself still not L1 after-cost |
| 2 | Multi-structure vs tunnel | **PASS** | Prior BAC width path stayed closed; P1 iron-butterfly scaffold, not single-leg/PCS thrash |
| 3 | Time bias axis | **PASS** | Explicitly deferred (prior merge seed was structure gap); not pretended |
| 4 | Direction/regime bias | **PASS** | Neutral-pin gate in sim + B3 yearly/canon soft-hold path used |
| 5 | Sims actually run | **PASS** | Paths present; metrics re-read from JSON (not vibes) |
| 6 | Quality bar before capital | **PASS** | B3+B4 + quality_bar lab; both IB fail B4; `l1=[]` |
| 7 | ONE closed NEXT | **PASS** | Fixed-$ per-leg half-spread cost axis across PCS/IC/IB; reject-not-tune |
| 8 | No live/shadow promotion | **PASS** | Paper/research only; statuses stay candidate/testing |

## Evidence re-read (not re-run)

| Artifact | Status |
|---|---|
| `.cache/platform/quality_bar_lab_2026-07-11T1629.json` | present; `l1_hyp_ids=[]` |
| `.cache/platform/stress_cost_lab_2026-07-11T1629.json` | present; 5% slips match table |
| `.cache/platform/stress_regime_lab_2026-07-11T1629.json` | present; regime_hold soft true both IB |
| `.cache/platform/research_reports/2026-07-11_run28.md` | 22/23 scored; TSLA CSV parse error |
| `.cache/platform/evolve_audit.jsonl` last | `2026-07-11T23:34:07+00:00` applied pop36 |
| `trader_platform/research/iron_butterfly_sim.py` + `tests/test_iron_butterfly_sim.py` | present |
| evolve/B3/B4/smoke wiring | present in evolve_tick / smoke_test / strategy_dna |
| coverage LATEST | catalog **17**; `iron_butterfly` n_hyps=4 candidate |

### Quality table (verified)

| hyp | ml | window max DD | dense-neg | B3 | 5% slip | L1 |
|---|---:|---:|---:|---|---|---|
| leader `b195f5fe` | 76.32 | 74.85 | 5 | hold | n13 / −18.32 NULL (soft cost_hold) | no |
| SMCI IB `8444c65b` | 130.59 | 230.72 | 5 | hold | n251 / −29018.86 REJECT | no |
| TSLL IB `486c4c32` | 30.86 | 81.70 | 3 | hold | n180 / −12172.17 REJECT | no |

Cost summaries also show SMCI 5y baseline **SHIP** +333.93 → 5% REJECT; TSLL 5y baseline **NULL** +239.9 → 5% REJECT. Cadence blow-up (n7–8 at 2y mid-mark → n180–251 at 5% over 5y) is real sensitivity evidence, not “observed spreads = 5%.”

## Nits (non-blocking)

1. **Research “top eight”:** run28 composite ranks MU #3 (oversized). Executor top-eight list skipped MU and started PLTR as #3. Same class of ranking shorthand as prior wakes; does not change IB rejects.
2. **“Focused iron_butterfly” pop36:** last apply was mixed structure counts (IB≈19, IC≈8, short_put≈7, plus CCS/wheel). Claim “no 2y iron-butterfly SHIP” still holds; overall `n_ship=2` are not IB L1 evidence. Known evolve-population pitfall — judge by DNA structure, not pop label.
3. **TSLL IB 2y vs 5y language:** 2y NEEDS_MORE_DATA n7 is sparse; 5y full-history NULL with soft B3 hold is the correct stress framing. Executor quality table is the right bar.

## Judgment on progress claim

- Progress type **P1 + P3** accepted.
- Progress score **4/5** accepted (real gap closed + honest falsify; zero L1 edge).
- Honesty **L0 BUILD** accepted — no non-vacuous after-cost SHIP + competitive ml/dd anywhere; capital path not expanded; no real-account readiness.

Relative quality ref remains `b195f5fe` (soft 5% loss, not L1).

## NEXT SEED (challenger keep / slight tighten)

Next BUILD only: implement a **simulator-wide fixed-dollar per-leg half-spread** cost axis (conservative option tick / half-spread dollars, not % of gross legs), then run one uniform B4-style table on representative **PCS + IC + iron_butterfly** DNA (include leader `b195f5fe` + one IC + SMCI/TSLL IB). **Reject rather than tune DNA** if observed-like fixed costs remain negative or cadence-catastrophic. No BAC width re-polish; no new multi-leg scaffold thrash until this cost axis exists.

GATES: none
MOA_CHALL_DONE
