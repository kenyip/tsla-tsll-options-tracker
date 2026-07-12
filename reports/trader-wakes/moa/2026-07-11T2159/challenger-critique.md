# MOA BUILD lab challenger critique — 2026-07-11T2159

CHALLENGER: Grok 4.5 (read-only)
PHASE: BUILD
SLEEVE: 3000
MODE: paper/research only — no evolve --apply, no broker, no arm, no shadow promote

## Rubric

| # | Criterion | Verdict | One line |
|---|---|---|---|
| 1 | Goal progress | **PASS** | New defined-risk sim class + pure-pop + immediate absolute-gate reject raises discovery capability without fake L1. |
| 2 | Creativity / independence | **PASS** | Bearish 1x2 put-ratio (valley loss + convex crash) is a real payoff family vs prior credit-IB/BWIB; prior NEXT kept for justified reason. |
| 3 | Claim validity | **PASS** | Proxy BS marks labeled; one-date archive not used for L1; claims fail closed on absolute ml/DD/B3/B4. |
| 4 | Evidence / test quality | **PASS** | Dated evolve/regime/cost/fixed JSON match metrics; 4/4 behavioral tests re-ran OK (valley loss, adverse cost, bullish fail-close, structure purity). |
| 5 | Falsification | **PASS** | Explicit L1 gates; SMCI cost-survives but B3/ml/DD reject; BAC B3-holds but 5% NULL and DD~2× gate; family off capital path. |
| 6 | Capital honesty | **PASS** | No living leader; soft `preferred_under_cost=SMCI` is not a seat; max_lots arithmetic disclosed; 1-lot research posture. |
| 7 | Research freedom | **PASS** | Observed archive block did not freeze unrelated proxy scaffold; freedom audit honest. |
| 8 | ONE NEXT seed | **PASS** (tighten) | Keep BAC management grid with hard reject-family stop; do not thrash SMCI vanity path or re-open after one fail cycle. |

**Overall: PASS 8/8**

## Verified claims (recomputed)

Paths exist and parse:

- `.cache/platform/put_ratio_backspread_evolve_lab_2026-07-11T2159.json` — n_pop=22, n_ship=6, n_null=8, n_reject=8, structures exactly `{put_ratio_backspread}`, created_hyps=8
- `.cache/platform/stress_regime_put_ratio_lab_2026-07-11T2159.json`
- `.cache/platform/stress_cost_put_ratio_lab_2026-07-11T2159.json`
- `.cache/platform/fixed_cost_put_ratio_lab_2026-07-11T2159.json`

| Hyp | Full | B3 | B4 @5% | Fixed $0.01/leg | L1 |
|---|---|---|---|---|---|
| SMCI `86a2d26a` | n71 / +3532.07 / DD 617.17 / ml 365.81 | FAIL (worst −467.12; window max DD 530.47; dense-neg 2; regime_hold=false) | SHIP n66 / +1842.02 | SHIP n71 / +3200.48 / DD 687.83 | **REJECT** (ml>300, DD≫75, B3 fail) |
| BAC `967b8c06` | n64 / +851.28 / DD 149.68 / ml 119.06 | soft hold (worst −51.58; window max DD 149.86; dense-neg 1) | NULL n62 / −81.48 | NULL n64 / +576.58 / DD 197.70 | **REJECT** (5% non-positive; DD>75) |

Cost preferred soft rank = SMCI — **not** capital seat (executor correct).

Code/tests: `trader_platform/research/put_ratio_backspread_sim.py`, catalog entry, evolve/B3/B4/fixed dispatch, `tests/test_put_ratio_backspread_sim.py` 4/4 pass. Coverage: 19 structures; 8 put_ratio hyps candidate-only. Income coverage gap text matches doctrine.

## Challenges / corrections

1. **Do not over-read fixed-cost BAC “+$576.58”.** Fixed $0.01/leg verdict is **NULL**, not SHIP; PnL positive with worse DD ($197.70). Keep language: fixed-cost soft-positive, not after-cost quality.
2. **SMCI after-cost SHIP is interesting but not near L1.** Unlike iron-butterfly cost collapse, 5% survival is real *within proxy*. Still fails hard: ml $365.81 > $300, window DD $530.47, B3 fail (worst −$467). No management polish of SMCI until those absolute gates can even be approached — valley width + SMCI vol path likely structural.
3. **Soft `preferred_under_cost` is ranking noise.** Same pattern as prior BWIB preferred_under_cost ≠ seat.
4. **max_lots=2/3 is open-risk arithmetic only.** Research posture remains 1 lot; never promote multi-lot on vanity full-history PnL.
5. **NEXT thrash risk (mild).** BAC already fails non-vacuous after-cost (5% NULL −$81) and DD ~2× absolute gate. One `defined_loss_exit_frac × dte_stop` grid + OOS is acceptable as management-axis last look; **if no row is dense after-cost positive AND ml≤300 AND window DD≤75 AND dense-neg≤5 AND OOS dense → close put-ratio capital path for this cycle** and next wake must pick an *independent* axis (not SMCI retune, not free put-ratio re-evolve).
6. **Readiness phase-decision footer is stale** (still claims archive substrate blocked evolve this wake). NEXT line itself is correct; challenger does not rewrite full readiness body (NEXT not wrong). Future merge/exec should refresh phase-decision text.
7. **Executor “10/10 targeted” not re-audited beyond put_ratio 4/4.** Accept residual claim; no contradiction found. Full suite 47/48 with pre-existing PMCC fixture failure is consistent with recent wakes.

## What was *not* claimed (good)

- No live / shadow / agentic arm
- No living quality leader restoration
- No observed-surface calibration from 1-date archive
- Proxy / BS / no assignment realism labeled

## Progress judgment (challenger)

- Type: P1 new sim class + P3 quality falsify
- Score: **4/5** (agree with executor)
- Honesty: **L0 BUILD** — capability + decisive capital-path rejection; not paper-ready; not real-account ready
- Living quality leader: **none** (`b195f5fe` historical only)

## ONE merged NEXT SEED

One exact structure-pure grid on BAC `hyp_dna_bac_put_ratio_backspread_967b8c06` over `defined_loss_exit_frac × dte_stop`, with mid + 5% slip and chronological OOS on any non-vacuous after-cost-positive row. Promote nothing. Reject the put-ratio family for this cycle unless: dense positive@5%, ml≤300, window max DD≤75, dense-neg≤5, and dense OOS. If reject: next wake **must** leave put-ratio capital search (keep sim as research tool) and choose an independent BUILD axis. RTH parallel unchanged: next distinct NY market date append all-expiration TSLL archive 1→2/3; no provider hist sim before 3/3.

GATES: none. Paper/research only.

MOA_CHALL_DONE
