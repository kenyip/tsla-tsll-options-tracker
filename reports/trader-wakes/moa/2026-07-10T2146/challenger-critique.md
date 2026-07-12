# MOA BUILD Lab challenger critique — 2026-07-10T2146

PHASE: BUILD
SLEEVE: $3,000
ROLE: Grok 4.5 challenger (read-only; no evolve --apply; no broker/live/arm)
EXECUTOR: GPT 5.6 Sol closeout + wake `2026-07-10T2146-moa-exec.md`

## Verdict

**PASS 8/8 on the loop rubric.** Executor closed a coherent Axis-E loop (calendar sim realism + non-vacuous falsify), cited real artifacts, rejected capital expansion honestly, and left **one** BUILD seed. Income edge for real trades did **not** improve — and that is the correct judgment.

## Rubric

| # | Item | Result | One line |
|---|---|---|---|
| 1 | Income goal honesty ($3k / after-cost, not vanity $) | **PASS** | Calendar full-history SHIPs ($666–$1,370) rejected; L0 only; leader soft loss at 5% still not L1 |
| 2 | Multi-structure search vs tunnel | **PASS** | Not TSLL-PCS polish: free catalog + calendar realism across TSLL/SMCI/BAC; single-leg evolve toys not promoted |
| 3 | Time bias as real axis or deferred gap | **PASS (deferred)** | Axis E treated calendar term/skew as time-structure realism; weekday/session still open gap (coverage) |
| 4 | Direction/regime as real axis or deferred gap | **PASS (deferred)** | B3 run on leader + calendars; no dedicated PCS/CCS/IC regime scoreboard this wake — ok given one-loop rule |
| 5 | Sims actually run (paths) | **PASS** | Verified stress/OOS/research/evolve paths; metrics match closeout table |
| 6 | Quality bar / B3+B4 before capital talk | **PASS** | All three calendars fail non-vacuous B4; no capital-path expansion; soft cost_hold ≠ edge on leader |
| 7 | ONE closed NEXT seed | **PASS** | Minimal sleeve-fit `diagonal_spread` sim → smoke → one evolve + B3/B4 reject-unless-beats-bar |
| 8 | No live/shadow promotion | **PASS** | candidate-only hyps; no arm/shadow/live language beyond hard stops |

## Evidence verification (challenger re-read)

Sources exist and numbers reconcile with executor tables:

| Claim | Source | Challenger check |
|---|---|---|
| Research run19 top TSLL,SMCI,TSLA,… | `.cache/platform/research_reports/2026-07-11_run19.md` | file present |
| Evolve apply 04:49Z; calendars `34f2b2c5` / `917fff50` / `8ccac90f` | `evolve_audit.jsonl` + `hypotheses.yaml` | created_hyps include all three; status candidate |
| Leader ml $76.32 / window DD $74.85 / regime_hold true | `stress_regime_lab_2026-07-10T2146.json` | match |
| TSLL cal ml $110.41 n110 pnl $666.69 DD $121.55 dense_neg 3 hold | same | match |
| SMCI cal ml $226.21 n152 pnl $1370.71 DD $344.90 dense_neg 4 hold | same | match |
| BAC cal ml $43.30 n148 pnl $54.64 DD $170.83 dense_neg 9 hold | same | match |
| 5% slip n/pnl: leader 13/−18.32; TSLL 93/−266.85; SMCI 124/−1511.58; BAC 128/−742.30 | `stress_cost_lab_2026-07-10T2146.json` | match; cost_hold only on leader (soft) |
| OOS test: TSLL 46/$479.53/$30.93; SMCI 66/$824.21/$134.56; BAC 60/−47.78/$170.83 | `calendar_oos_lab_2026-07-10T2146.json` | match |
| Front/back IV + put_skew in sim DNA | `calendar_sim.py`, DNA configs | present (e.g. front 1.05 / back ~0.93–0.95) |

**Judgment upheld:** positive OOS baseline marks on TSLL/SMCI calendars are **not** income readiness while 5% slip stays dense and deeply negative. BAC fails both OOS and B4. Class-level reject of the current underlying-IV-proxy calendar path is honest.

## Challenges / nits (not FAIL)

1. **Progress 4/5 is right; do not read auto scoreboard as L1.** `build-progress-LATEST` still heuristics some prior duals at 5/5 from keyword soup — ignore for live confidence. Executor’s **4/5 + L0** is the truthful score for this stamp.
2. **BAC “SHIP” on 2y evolve was weak** (audit score ≈ −11.6, thin edge) — still correctly stress-tested then rejected. No overclaim.
3. **Free pop36 still emitted single-leg SHIPs** (research toys). Acceptable as long as they stay off capital path (they did). Prefer defined-risk-weighted population next if diagonal work is the seed.
4. **NEXT diagonal risk:** another multi-expiry BS proxy without observed surfaces can re-learn the calendar lesson. Keep executor’s reject bar: synthetic smoke + one evolve + **non-vacuous B3/B4**; baseline SHIP alone is not progress toward L1. If diagonal dies the same way, next seed should pivot to **defined-risk credit edge hunt (PCS/CCS/IC time/direction)** or **B6 paper on leader**, not infinite assumed-IV knobs.
5. **Time/direction scoreboards not advanced this wake** — correct under one-loop freedom; still open gaps on coverage map.
6. **Did not re-run `just platform-smoke`** (read-only budget). Code paths for term/skew are present; take smoke PASS as executor-reported unless next BUILD hits red.

## Income / readiness honesty

- **PROGRESS TYPE:** P1 sim realism + P3 quality falsify — **score 4/5** (agree).
- **L0–L4:** **L0 BUILD only** (agree). No DNA has non-vacuous **positive** after-cost edge + competitive ml/dd. Leader remains soft loss at 5% slip. B6 thin; B7 absent; account unfunded.
- **Capital path:** unchanged = `hyp_dna_tsll_put_credit_spread_b195f5fe` (relative example only).
- **Calendar class:** research-park; do not retune assumed multipliers as readiness theater.

## ONE merged NEXT seed

See `merged-next-seed.md` — keep executor seed, with reject-as-success and no capital talk without B3+B4.

Hard stops held by challenger: no evolve --apply, no live/broker/arm/shadow auto-promote.

MOA_CHALL_DONE
