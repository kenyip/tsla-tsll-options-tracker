# MOA BUILD lab challenger critique — 2026-07-11T2121

CHALLENGER: Grok 4.5 (read-only judgment)
PHASE: BUILD · SLEEVE: 3000 · MODE: paper/research only
SOURCE: executor-closeout.md + cited lab JSON + live code/registry inspects

## Rubric (PASS/FAIL + one line)

1. **Goal progress — PASS.** Built and falsified a new defined-risk structure class; catalog 17→18 and a decisive capital-path reject improve discovery odds more than another archive no-op on a closed Saturday.
2. **Creativity and independence — PASS.** Broken-wing credit iron butterfly is a real directional/asymmetric extension of symmetric IB, not a TSLL-PCS tunnel; superseding same-date archive recapture is justified.
3. **Claim validity — PASS.** Explicit BS-proxy boundary; mid-run population-purity asymmetry flaw fixed and restressed; observed-provider claims correctly left blocked.
4. **Evidence — PASS (with notes).** Regime/cost/fixed JSON metrics match claims; hyps remain `candidate`; soft `preferred_under_cost` is XOM `34120077` and is not a seat. Evolve pop mixed structures (not pure BWIB).
5. **Falsification — PASS.** Absolute L1 gates stated and applied; non-vacuous 5% B4 + $0.01/leg negative control + window-DD>$75 all fire; family REJECT is honest.
6. **Capital honesty — PASS.** No living leader; no capital seat; no shadow/live; five BWIB hyps research-only; b195f5fe not re-seated.
7. **Research freedom — PASS.** Observed-data density block did not freeze an independent proxy structure experiment.
8. **ONE NEXT seed — PASS (tightened).** Put ratio backspread is allowed creative freedom; constrain defined-risk math, pure population, and stop-if-same-B4-collapse pattern.

**Overall: PASS 8/8** (evidence notes do not flip any criterion).

## Verified evidence (read-only)

### Loop choice
- Executor chose **P1 + P3**: `broken_wing_iron_butterfly` scaffold + immediate B3/B4/fixed-cost falsify.
- Prior readiness NEXT (append TSLL archive on next distinct NY RTH date) correctly **superseded for this evening**: markets closed Sat 2026-07-11; same-date recapture cannot raise `provider_backtest_eligible`. Observed path remains blocked for provider-backed promotion only.

### Code / catalog
- `STRUCTURE_CATALOG["broken_wing_iron_butterfly"]` present (`trader_platform/strategy_dna.py`) with wider-put / narrower-call legs and widest-wing-minus-credit risk language.
- `iron_butterfly_sim.pick_iron_butterfly_entry` enforces `lower_steps = max(lower_steps, upper_steps + 1)` for broken-wing after strike-grid rounding (asymmetry invariant).
- `tests/test_iron_butterfly_sim.py::test_broken_wing_has_wider_put_side_and_defined_worst_case` present; `python -m unittest tests.test_iron_butterfly_sim` → **3/3 OK** (challenger re-ran). Executor “6/6 targeted” not re-expanded; family sim tests green.
- Coverage report `reports/readiness/income-coverage-LATEST.md` (2026-07-11T2129): **18** structures, **226** hyps, quality leader **none**, 5 BWIB candidates.

### Evolve population (`.cache/platform/broken_wing_evolve_lab_2026-07-11T2121.json`)
- `n_population=24`, symbols 8 (TSLL, SMCI, PLTR, NFLX, BAC, XOM, MU, TSLA), `n_ship=4`, `applied=true`.
- SHIP set is **not pure BWIB**: 1× `short_put_credit` TSLL + 3× BWIB (SMCI/XOM/SMCI). Also created single-leg / other DNA noise in `created_hyps` / `updated_hyps`.
- **Note (not a capital claim):** population purity for “focused structure lab” is partial — skill pitfall. Judgment on stressed BWIB DNA still valid because exact stresses named those hyps.

### B3 (`.cache/platform/stress_regime_broken_wing_lab_2026-07-11T2121.json`) — metrics match

| Hyp | full n / pnl | max_loss | max_window_dd | dense_neg (n≥3) | regime_hold |
|---|---:|---:|---:|---:|---|
| SMCI `0af49a8c` | 78 / +600.68 SHIP | 131.23 | 231.89 | 6 | soft True |
| XOM `34120077` | 60 / +665.85 SHIP | 256.38 | 523.09 | 2 | soft True |
| SMCI `9279bfed` | 84 / +599.77 SHIP | 130.12 | 191.84 | 5 | soft True |

All fail absolute L1 on **window DD > 75** (and `0af49a8c` also dense_neg 6 > 5). Soft regime_hold is not L1.

### B4 (`.cache/platform/stress_cost_broken_wing_lab_2026-07-11T2121.json`) — metrics match
- 5% slip non-vacuous REJECT: `0af49a8c` n409 / −53378.96; `34120077` n72 / −6077.73; `9279bfed` n489 / −59918.18.
- Cadence explosion under % slip (classic multi-leg gross-leg sensitivity) — valid as **sensitivity rejection**, not “observed $5k loss.”
- `preferred_under_cost` = XOM `34120077` — **soft ranking only; not a capital seat** (executor did not promote; challenger pins the label).

### Fixed-dollar negative control (`.cache/platform/fixed_cost_broken_wing_lab_2026-07-11T2121.json`)
- $0.01 half-spread/leg ($8 RT four-leg): all three negative / high DD — matches executor (`0af` n80/−238.25 DD487.80; `xom` n60/−4.53 DD573.58; `927` n88/−177.85 DD456.51).

### Registry / capital
- Five BWIB hyps all **`candidate`**: `0af49a8c`, `34120077`, `9279bfed`, `6badce12`, `d9e5a501`.
- No living quality leader; capital path empty; no live/broker/arm/shadow in this wake residue.

## Challenges / corrections

1. **“Focused 24 DNA” was catalog-mixed, not BWIB-only.** One SHIP is undefined-risk short put. Do not count single-leg SHIP as structure-class evidence. Stressed trio still supports family REJECT.
2. **Soft `preferred_under_cost` must stay non-seat language** whenever cost script emits it (XOM here).
3. **Score 4/5 kept, not 5/5:** decisive reject + real scaffold, but still another multi-leg BS proxy collapse in the same pattern as symmetric IB / butterflies / debit verticals — learning is real, L1 proximity is not.
4. **NEXT seed (put ratio backspread) — allow with hard constraints:**
   - Classic 1×2 put ratio backspread can be **debit or credit**; max loss must be **closed-form and sleeve-capped** in sim (no naked short-put residual if long qty < short qty; use buy-more / sell-fewer only).
   - Enforce structure purity in the first evolve population (`--structures` / filter) so SHIP count is not polluted by single-leg toys.
   - Immediate absolute L1: non-vacuous after-cost SHIP + B3 soft-hold + max_loss ≤300 + window max DD ≤75 + dense_neg ≤5; plus $0.01/leg fixed control.
   - **If** baseline mid-mark SHIP again collapses at 5% and fixed $0.01 like IB/BWIB, **stop scaffolding more 3–4 leg credit multi-legs for one cycle** and pivot to (a) next distinct RTH archive day for observed density, or (b) management/time axis on already-built verticals under absolute gates — not infinite proxy-class thrash.
5. **Archive NEXT is not wrong** — it remains the observed-data obligation on the next NY RTH session. It was correctly not the highest-information Saturday evening BUILD action.

## Judgment on executor claims

| Claim | Verdict |
|---|---|
| Family capital-path REJECT | **AGREE** |
| No L1 / no living leader | **AGREE** |
| Proxy-only; not paper/live ready | **AGREE** |
| Progress P1+P3 score 4/5 L0 | **AGREE** |
| Progress type honesty | **AGREE** — capability + falsify, not edge |

## Merged progress close

- Type: **P1 new sim class + P3 quality falsification**
- Score: **4/5**
- Honesty: **L0 BUILD** — useful asymmetric IB capability + decisive family reject; not paper-ready; not real-account ready

## ONE merged NEXT SEED

Build the smallest paper-only **put ratio backspread** scaffold (sell 1 higher-strike put, buy 2 lower-strike puts) with **closed-form defined max loss**, catalog/evolve/B3/B4/fixed-$ wiring, structure-pure population, and immediate reject unless absolute L1 gates pass; if the class collapses like BWIB/IB under non-vacuous 5% and $0.01/leg, stop further multi-leg credit scaffolds this cycle and resume archive density on the next distinct NY RTH date.

GATES: none. No evolve `--apply` by challenger. No live / broker / arm / shadow auto-promote.

MOA_CHALL_DONE
