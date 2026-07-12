# MOA BUILD lab challenger critique — 2026-07-11T1826

ROLE: Grok 4.5 challenger (read-only)
PHASE: BUILD · SLEEVE: $3000
HARD STOPS OBSERVED: no evolve --apply; no broker/live/arm/shadow

## Executive judgment

**PASS 8/8.** Executor closed a real P1 realism boundary (injectable actual expiry/right-specific strike grid for PCS/CCS/IC, fail-closed required mode, labeled synthetic default) plus one honest P3 falsify. Metrics match dated stress JSON. Capital path stays empty. L0 BUILD only. NEXT seed is one closed loop and correctly blocks archive-blind evolve thrash.

## Evidence verified

| Claim | Check | Result |
|---|---|---|
| ContractGridProvider + required fail-close | `pcs_sim.py` `ContractGrid`/`ContractGridProvider`, `_available_contract`, `require_contract_grid`; metrics mode `required_observed` | **pass** |
| Fixture tests | `tests/test_pcs_expiry_grid.py` re-run | **7/7 pass** (selection, missing grid/right/wing, zero-coverage backtest) |
| Evolve tick | `.cache/platform/evolve_audit.jsonl` last row `2026-07-12T01:33:36+00:00` | **pass** — pop36, symbols TSLL/SMCI/PLTR/NFLX/BAC/XOM/MU/TSLA, n_ship=5 |
| SHIP set | audit evidence paths | SMCI calendar, NFLX calendar, NFLX CSP, BAC wheel, TSLA butterfly |
| Single-leg toys not capital-seated | CSP/wheel left research-only | **pass** |
| B3/B4/quality artifacts | dated lab JSON exist | **pass** |
| Quality numbers | match executor table | **pass** (see below) |
| `l1_hyp_ids` | quality JSON | `[]` · decision `REJECT_ALL_CAPITAL_PATH` |
| No live/shadow promote | closeout + readiness | **pass** |

### Quality table (challenger-checked)

Historical comparison bar only (not a living capital seat): max_loss $76.32 / window DD $74.85 from pre-listed-expiry b195f5fe.

| hyp | full | ml | window DD | dense-neg | B3 | 5% | L1 |
|---|---:|---:|---:|---:|---|---|---|
| SMCI cal b11a8ff0 | n145 / +$1077.14 | $189.00 | $308.74 | 3 | soft hold | n122 / −$1401.20 REJECT | no |
| NFLX cal 307c7de5 | n158 / +$908.58 | $137.37 | $252.31 | 5 | soft hold | n132 / −$1261.38 REJECT | no |
| TSLA fly d13ef44d | n87 / +$85.33 | $21.25 | $36.01 | 5 | soft hold | n529 / −$94077.49 REJECT | no |
| TSLL PCS b195f5fe | n62 / +$42.54 | $75.35 | $88.39 | 5 | soft hold | n13 / −$13.18 NULL | no |

Notes that match doctrine pitfalls:
- Butterfly is competitive on proxy ml/dd then **cadence-explodes** under slip (n87 → n529) — valid B4 sensitivity reject, not a tune target.
- b195f5fe `cost_hold=true` / `preferred_under_cost` is **soft NULL@5%**, not non-vacuous after-cost SHIP and not a capital seat.
- Window DD $88.39 still fails the historical $74.85 bar.

Coverage scoreboard (`income-coverage-LATEST.md` 1839): quality leader hint correctly `none`; cost-realism gap text includes injectable provider + archive density remaining.

## Rubric

1. **Income goal honesty** — **PASS.** $3k / 1-lot / after-cost / no vanity promote; sleeve toys called toys.
2. **Multi-structure search vs tunnel** — **PASS.** Multi-name free pop after scaffold; calendars + butterfly stressed; not TSLL-PCS monomania.
3. **Time bias axis** — **PASS (deferred with gap).** Explicitly chose higher-leverage contract-grid realism; time lab already exists (weekday/DTE grid + transient B3+B4). Session-time still open but not this wake’s priority.
4. **Direction/regime bias** — **PASS (deferred with gap).** B3 yearly/6m/canon windows used for falsify; direction scoreboard already built; no fake direction promote.
5. **Sims actually run** — **PASS.** Paths: evolve_audit, `stress_regime_lab_2026-07-11T1826.json`, `stress_cost_lab_…`, `quality_bar_lab_…`, evolve_backtests for SMCI/NFLX calendar + TSLA butterfly.
6. **Quality bar / B3+B4 before capital path** — **PASS.** Clear `REJECT_ALL_CAPITAL_PATH`; empty `l1_hyp_ids`.
7. **ONE closed NEXT seed** — **PASS.** Archive rows → date-aware `ContractGridProvider` + coverage counters + one fail-closed TSLL snapshot replay smoke; no evolve without historical entry-date coverage.
8. **No live/shadow promotion** — **PASS.**

## Challenges (non-blocking)

1. **Soft preferred ≠ seat.** Cost lab still lists `preferred_under_cost = b195f5fe`. Correct as soft survivor among rejects only; do not re-label capital path from that field.
2. **Targeted “16/16” not fully re-run here.** Challenger re-ran expiry-grid suite **7/7**. Broader related-suite claim is accepted as executor-local; core provider tests are green.
3. **Archive wiring honesty.** Existing TSLL snapshot is one as-of cross-section (~70 rows). Fail-closed replay smoke is the right success metric; do **not** claim historical entry-date density from a single snapshot. If counters show insufficient multi-date coverage, stop and report density blocker — do not retune DNA.
4. **Synthetic default remains discovery truth.** Provider is an injection boundary, not observed evidence until wired and dense. Executor labeled this correctly; keep that language in readiness.
5. **Score 4/5 is fair, not 5.** Real P1+P3 closed loop, but L1 still empty and observed-data path still incomplete.

## Progress score (challenger)

- Type: **P1 + P3**
- Score: **4/5**
- Honesty: **L0 BUILD** (no L1 DNA; no capital path; not real-account ready)
- Drift: low — took prior NEXT, did not thrash free single-leg-only polish as the main claim

## Merged NEXT (one)

Wire normalized archived option-quote rows into a date-aware `ContractGridProvider`, emit provider coverage counters (dates covered / required / missing rights-wings), and run one fail-closed replay smoke against the existing TSLL snapshot. Success = correct fail-closed behavior + honest counters. Do **not** evolve again unless the provider has multi-date historical entry coverage dense enough for non-vacuous B3/B4.

MOA_CHALL_DONE
