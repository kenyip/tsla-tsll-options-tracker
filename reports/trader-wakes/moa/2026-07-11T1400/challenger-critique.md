# MOA challenger critique — 2026-07-11T1400 (Grok 4.5)

Role: read-only judgment. No evolve --apply. No broker / live / shadow arm.

## Orient

- Prior NEXT (1000 merge): multi-hyp cost-aware PCS/CCS time grid; B3 only non-vacuous positive@5%; reject unless window DD ≤ $74.85 and dense-neg ≤ 5.
- Executor: Axis B / P2+P3 — multi-hyp 5% time grid + exact transient B3+B4; free pop36; dated B3+B4 on leader + three new DR SHIPs + BAC time row; quality table; L0; NEXT resize BAC Fri 7d width toward $0.50.
- Phase: BUILD · sleeve $3000 · quality leader remains relative only (not L1).

## Evidence verification (read-only)

| Claim | Verified? | Path / note |
|---|---|---|
| Research run26 23/23 | YES | `.cache/platform/research_reports/2026-07-11_run26.md` |
| Top eight as written | YES (Top symbols) | TSLL, SMCI, TSLA, PLTR, AAPL, AMD, ARM, QQQ. Capital table still lists MU high by another sort — not used as top8 here. |
| Only TSLL/SMCI naked fit_3k | YES | run26 capital table |
| Evolve pop36 applied @ 21:01Z | YES | `evolve_audit.jsonl` @ `2026-07-11T21:01:08+00:00` — applied=true, n_population=36, n_ship=3; symbols TSLL/SMCI/PLTR/NFLX/BAC/XOM/MU/TSLA |
| New DR SHIPs calendar/butterfly/BAC PCS | YES | quality + B3/B4 labs: `5e575b61`, `e34563aa`, `5f52fa0e` |
| Multi-hyp 864-row 5% grid | YES | `time_bias_multi_cost5_lab_2026-07-11T1400.json` — 4 hyps × 216 = 864; slippage_pct=0.05 |
| Grid hyps include PCS+CCS | YES | b195f5fe PCS, XOM CCS 77766a47, BAC CCS e6728888, BAC PCS 5f52fa0e |
| “PCS/CCS/IC” lab run | **NIT** | Tool supports IC; **this** artifact has **no IC** hyp (2 PCS + 2 CCS only) |
| Standout BAC Fri 7d / PT35 / stop5 | YES | ranked[0]: n189 / +$690.05 SHIP; max_loss≈$185.24 (grid) |
| PT35 is distinctive | **NIT** | Fri/7d/stop5 rows for PT 0.35/0.50/0.65 are **identical** (same n/pnl/ml) — PT not binding under dte_stop=5 |
| Exact transient B3+B4 tool + run | YES | `pcs_time_variant_stress.py` + `time_bias_bac_pcs_variant_stress_2026-07-11T1400.json` |
| Variant dense + cost-positive | YES | full n191/+$963.04; slip5 n189/+$690.05 SHIP; slip10 +$415.80 SHIP; B3 regime_hold; dense-neg=2; window max_dd **87.29** |
| Variant misses L1 ml/dd | YES | ml **184.55** / window DD **87.29** vs leader **76.32 / 74.85**; quality decision REJECT_L1… |
| Base BAC PCS width=$2 | YES | B3 config + variant_config `spread_width: 2.0` |
| New base SHIPs cost-rejected | YES | calendar 5% −242.09; butterfly 5% −43784.78; BAC base 5% −176.36; all cost_hold false except leader soft |
| Leader still below L1 | YES | ml 76.32 / win DD 74.85 / dense 5 / B3 hold / slip5 n13 −18.32 NULL soft cost_hold |
| `l1_hyp_ids=[]` | YES | `quality_bar_lab_2026-07-11T1400.json` |
| Coverage multi-hyp time gap closed | YES | income-coverage-LATEST: multi-hyp DTE/PT/stop + weekday + exact transient B3+B4; session-time still missing |
| No capital / live / shadow promote | YES | L0 BUILD; BAC row unregistered; NEXT width-resize only |

### Recomputed quality table (from lab JSON)

| hyp / variant | ml $ | window DD $ | dense neg | B3 | 5% n / pnl $ | decision |
|---|---:|---:|---:|---|---:|---|
| TSLL PCS `b195f5fe` | 76.32 | 74.85 | 5 | hold | 13 / −18.32 | RELATIVE_LEADER_BELOW_L1_AFTER_COST_NEGATIVE |
| TSLL calendar `5e575b61` | 81.94 | 144.46 | 6 | hold | 97 / −242.09 | REJECT_COST_AND_ML_DD |
| MU butterfly `e34563aa` | 17.93 | 43.05 | 2 | hold | 572 / −43784.78 | REJECT_COST |
| BAC PCS `5f52fa0e` | 187.54 | 508.70 | 6 | hold | 802 / −176.36 | REJECT_COST_AND_ML_DD |
| BAC Fri 7d / PT35 / stop5 (transient) | 184.55 | 87.29 | 2 | hold | 189 / +690.05 | REJECT_L1_MAX_LOSS_AND_WINDOW_DD_WORSE_THAN_LEADER |

`l1_hyp_ids=[]`. Executor correctly used **B3 window max_dd** (87.29), not full-history cost-grid max_dd alone (123.44 at 5%).

## RUBRIC

1. Income goal honesty — **PASS** — $3k / after-cost; strongest dense +$690@5% still refused on competitive ml/dd; no vanity capital seat; L0 explicit.
2. Multi-structure search vs tunnel — **PASS** — multi-hyp PCS+CCS time lab + falsify calendar/butterfly/BAC PCS; free pop36 mixed single-leg toys but not promoted (nit). Not monomania on TSLL PCS alone.
3. Time bias axis — **PASS** — multi-hyp DTE×PT×stop×weekday@5% closed prior seed; exact transient B3+B4 added. Session-time still open gap (honest).
4. Direction/regime bias — **PASS** — deferred as primary build; CCS included in multi-hyp grid (XOM+BAC); B3 windows on all falsified rows + prior direction scoreboard (0036).
5. Sims actually run — **PASS** — research + evolve_audit + 864-row grid + exact variant stress + dated regime/cost/quality JSON; metrics recompute match.
6. Quality bar B3+B4 before capital — **PASS** — all new base DR SHIPs fail; BAC time row fails strict L1 ml/dd despite non-vacuous after-cost SHIP (even @10%); leader not L1.
7. ONE closed NEXT seed — **PASS** — single BUILD loop: BAC Fri 7d width resize + exact B3+B4 reject-unless bar (kept with light tighten below).
8. No live/shadow promotion — **PASS**.

**TOTAL: PASS 8/8**

## Nits (non-blocking)

1. **“PCS/CCS/IC” overstates this run.** Artifact hyps are 2 PCS + 2 CCS; no iron_condor row in the 864. Capability ≠ run.
2. **PT35 label is non-identifying** at Fri/7d/stop5 — PT 0.35/0.50/0.65 identical. Prefer fixing PT=0.35 as a label, not as an optimized knob.
3. **Evolve symbols ≠ research top8** (NFLX/BAC/XOM/MU in; AAPL/AMD/ARM/QQQ out). Recurring free-pop habit; OK if defined-risk falsify stays the judgment layer.
4. **Free-catalog pop36 still emits undefined-risk toys.** Not promoted this wake — keep prefer defined-risk structures when P2/P3/P4.
5. **Width-only NEXT is leverage-correct for this after-cost row**, but reject thrash: if $1 and $0.50 both miss L1 or go vacuous@5%, **stop** width polish and leave a different next axis (do not invent more BAC PT knobs).

## Judgment

Keep executor evidence. Progress **P2+P3 score 4/5** (prior multi-hyp seed closed + densest non-vacuous after-cost income signal yet + honest L1 reject). Honesty **L0 BUILD only**. Capital path unchanged: `b195f5fe` relative quality example (soft cost_hold ≠ after-cost edge). BAC Fri time row is the best after-cost research residue found here — still **not** L1 and **not** registered.

**NEXT (kept + tightened):** width grid on the BAC Friday 7-DTE / stop5 / entry_weekday=Fri transient (`spread_width` $2 → $1 → $0.50), exact B3+B4 via `pcs_time_variant_stress` path; reject unless non-vacuous positive@5% **and** max_loss ≤ $76.32 **and** window max_dd ≤ $74.85 **and** dense-neg ≤ 5. Paper/research only.

MOA_CHALL_DONE
