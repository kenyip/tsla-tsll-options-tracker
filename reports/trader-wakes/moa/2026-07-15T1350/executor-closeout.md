# MoA BUILD executor closeout — 2026-07-15T1350

PHASE: BUILD / L0 discovery
SLEEVE_USD: 3000
ROLE: GPT 5.6 Sol executor; only writer
SESSION: postclose
PAPER_ONLY: true
OUTCOME: `FAMILY_CLOSED`
STRATEGY ADVANCEMENT: false; `F0_MECHANISM -> F0_MECHANISM`

## Strategy decision charter

- Economic edge mechanism: monthly index-option expiration may unwind dealer hedging and rebalance index exposure, creating a short, repeatable positive broad-index drift after third-Friday OPEX relative to an outcome-free same-month pre-OPEX Friday control.
- Candidate / family: `MONTHLY_OPEX_POST_EXPIRY_BULL_CALL_14D_V1` / `MONTHLY_OPEX_POST_EXPIRY_BROAD_INDEX_DRIFT`.
- Current evidence funnel: `F0_MECHANISM`; this wake could move only to `F1_TRAIN` under the discovery bar.
- Exact decision: `FAMILY_CLOSED`. Untouched holdout and option pricing remained unread/unrun.
- Predeclared falsifier: on the chronological first 60% of eligible non-overlapping monthly episodes, the equal-weight SPY/QQQ/IWM/DIA basket needed at least 48 episodes, positive five-session mean return after a labeled 10-bps round-trip underlying sensitivity, positive mean paired excess over the identical five-session window entered after the first same-month Friday, a positive one-sided 90% circular-block-bootstrap lower bound on paired excess, and zero chronology/control/overlap/integrity violations. Any failure closed the exact family at F0 without holdout inspection or option pricing.

## Layered Edge Stack

- Market / underlying: equal-weight SPY, QQQ, IWM, and DIA adjusted-close panel; liquid broad-index ETF options were the eventual expression surface, while the shared basket avoided a single-index anecdote. The experiment was underlying-only.
- Forecast type: `timing` plus `direction_up` over the five completed sessions after monthly OPEX.
- Economic mechanism: expiration-related dealer hedge unwind and index rebalance flow might release temporary pressure after monthly index-option expiry.
- Option structure: future one-lot 14-DTE $2-wide bull call debit spread, conditional on later F1/F2 evidence; no option mark was permitted in this train-only F0 test.
- Intended Greeks: positive delta and gamma with bounded debit risk; modest positive vega.
- Dangerous unintended Greeks: negative theta if drift is late/absent, volatility crush, and gap/path loss up to the paid debit.
- Regime envelope: only the next completed session after the adjusted third-Friday monthly OPEX label, held five sessions; all other calendar windows stand aside. The frozen F0 family was unconditional across trend/volatility regimes and earned no broader regime claim.
- Entry trigger: outcome-independent calendar label; identify the third Friday, adjust to the latest available session on or before it, then enter on the next completed session. Control uses the first same-month Friday with identical next-session entry and five-session horizon.
- Exit / management: underlying evidence used a fixed five-session horizon. A future option plan would use a five-session time stop, 50% of spread maximum-value profit harvest, and 50% of debit loss cut; those rules remain untested and grant no authority.
- Risk / capital fit: future structural context only: `capital_fit_usd=200`, one-lot `max_loss_usd=200` at the $2-width structural ceiling before closing friction, `max_lots=1`; portfolio overlap rule is one global directional index risk unit with no simultaneous correlated broad-index spread.
- Evidence / falsifier: split/dividend-adjusted underlying panel; chronological 60% train / 40% reserved holdout; labeled 10-bps round-trip sensitivity; paired same-month calendar control; dependence-aware block bootstrap; exact falsifier above.
- Confidence / permission: `F0_MECHANISM`, BUILD/L0 discovery only. No L1, capital-seat, paper, shadow, arm, broker, or live authority.
- Stand-aside rule: no trade outside the single post-OPEX entry session; no future option action if the structure cannot be opened within the $200 structural cap, quote/liquidity evidence is unavailable, or the candidate remains below F3. This close now quarantines the exact family from unchanged reruns.

## Executor judgment

Executor-time canonical evidence was `reports/trader-wakes/moa/2026-07-15T1350/monthly-opex-post-expiry.json` at SHA-256 `249b3124b131c6a45d7eee21fe73f1117b12f56a953c979225209c6b504505b4`. Finalizer population-label clarification regenerated the substantively unchanged strategy payload at final SHA-256 `15359b3ddc99055e378c009c5c9bdf49e6f07cdbe1e29beefe1d2357bfbe7c52`; see `learning-promotion.md`. The adjusted-close common panel has 2,647 sessions from 2016-01-04 through 2026-07-15. The chronological train partition contains 74 non-overlapping monthly episodes from 2016-02 through 2022-04; 50 later blueprints from 2022-05 through 2026-06 remain outcome-unread.

| frozen train metric | result | gate |
|---|---:|---|
| post-OPEX basket mean after 10 bps | `+0.4000275589%` | pass |
| first-Friday control mean after 10 bps | `+0.0831803451%` | context |
| paired excess mean | `+0.3168472137%` | pass |
| paired excess median | `+0.2233612315%` | context |
| paired excess positive frequency | `54.05405405%` | context |
| paired excess circular-block-bootstrap LB90 | `-0.2541751435%` | **fail** |
| integrity violations | `0` | pass |

The point estimate was positive but uncertainty was too wide: the frozen one-sided 90% lower bound remained negative. That is the predeclared decisive failure, so the exact broad-index post-OPEX drift family closes at F0. Reading the reserved outcomes or pricing a bull-call spread after this train failure would be holdout leakage and rescue tuning.

Dominant failure mechanism: the post-OPEX basket did not establish positive, uncertainty-bounded incremental train drift over an outcome-free first-Friday control. The evidence does not prove negative drift; it proves that this exact unconditional five-session calendar mechanism is too uncertain for advancement under its frozen bar.

## Evidence validity and critique

- Chronology: entry is the next completed session after the holiday-adjusted calendar label; each exit is five sessions later. Controls finish before event entry, and one episode's control starts only after the prior event exits. Integrity violations are zero.
- Selection: blueprints depend only on the shared trading calendar. A synthetic +50% event-outcome shock leaves selected event/control dates unchanged.
- Partition: the first 60% of 124 blueprints was evaluated. The later 50 expose only dates and counts; `outcome_metrics_read=false`, `simulation_run=false`, and no episode outcomes are serialized.
- Provenance: yfinance `auto_adjust=True`; fixed SPY/QQQ/IWM/DIA panel; inner date join; no forward fill; per-source hashes are persisted. The CLI re-reads the materialized cache before measurement, and an independent invocation reproduced the complete substantive payload after excluding only `generated_at`.
- Costs: 10 bps is a labeled underlying round-trip sensitivity, not an option fill estimate. Because event and control receive the same additive cost, it cancels from paired excess; therefore the separate positive absolute-after-cost gate is necessary. No observed option cost, spread, fill, liquidity, assignment, or intraday-path claim is made.
- Dependence: a seeded circular block bootstrap with three-month blocks and 10,000 samples preserves short monthly dependence. It cannot repair the limited 74-episode train sample; the negative LB is treated as a close, not tuned away.
- Population: the basket is fixed and complete for four established broad-index ETFs, but present-day membership creates survivorship/listing bias and does not generalize to other indexes or option products. Shared basket construction also means four symbols are not four independent samples.
- Structure alignment: a bull-call debit spread would monetize the stated positive directional timing forecast with bounded loss. It was not priced because the underlying mechanism failed first.
- Path/capital: no option path, drawdown, Greek realization, or paid debit was simulated. `$200` is only the future $2-width structural ceiling; it is not evidence of an executable capital seat.
- Living comparison: readiness has no living leader and the capital path is empty, so this result is judged against the absolute discovery falsifier, not a stale reference.

## Search information versus strategy progress

Search information: the wake added a reusable calendar-only, holiday-aware, non-overlapping, paired-control, train/untouched-holdout event-study lab with strict provenance, cache-round-trip reproducibility, bootstrap uncertainty, option-stage fail-close, and behavioral/boundary/negative-control coverage.

Strategy progress: none. `MONTHLY_OPEX_POST_EXPIRY_BROAD_INDEX_DRIFT` remains at F0 and is closed against unchanged SPY/QQQ/IWM/DIA, first-Friday control, next-session entry, five-session horizon, 60/40 split, 10-bps sensitivity, and bootstrap specification. Reopening requires a genuinely new economic mechanism or evidence class, not a nearby calendar/control/hold mutation.

## Capital / readiness / authority

- Future structure: one-lot defined-debit `bull_call_debit_spread`, 14 DTE, $2 width.
- `capital_fit_usd=200`; one-lot `max_loss_usd=200` structural ceiling; `max_lots=1`.
- No L1, living leader, capital seat, B-check, registry, paper, shadow, funding, broker, arm, or live transition.
- `reports/readiness/LATEST.md` remains unchanged because phase and B checks did not change.
- If accepted into active epoch `2026-07-15-viable-path`, this is the third consecutive no-advance wake. Burst-stop/reassessment is required before more strategy-search volume.

Freedom audit: Trader independently validated the advisory OPEX seed as the highest-information materially different open mechanism after two epoch no-advances; the caller did not select symbol, structure, or DNA, and closed cadence/cross-section/VRP/TOM/session families stayed quarantined.

## Verification

- TDD red boundary: missing implementation failed import before implementation existed.
- Focused behavioral/boundary/negative-control test: `.venv/bin/python -m unittest tests.test_monthly_opex_post_expiry_train_lab` -> 7/7 `OK`.
- Shared event-study/bootstrap regressions: monthly OPEX + low-HV + momentum modules -> 20/20 `OK`.
- Changed-file compile: exit 0.
- Exact dependent experiment: `FAMILY_CLOSED`; 74 train episodes; one failed uncertainty gate; zero integrity violations; 50 holdout blueprints unread; option pricing calls zero.
- Independent unchanged-source substantive reproduction: `SUBSTANTIVE_REPRODUCTION_OK` excluding only `generated_at`; manual episode-mean recomputation agrees within floating-point tolerance.
- Full suite: `.venv/bin/python -m unittest discover -s tests` -> 304/304 `OK`.
- Platform smoke: `platform smoke OK`; `agentic_live` remained blocked at the Stage1 OAuth gate.
- Coverage refresh: 21 catalog structures / 246 hypotheses / 70 evolve artifacts / living leader none; `reports/readiness/income-coverage-2026-07-15T1359.md` written.

## One next seed

`SEARCH_BURST_STOP_REASSESS_2026-07-15`: if this close is accepted, stop the active epoch's three-wake no-advance search burst. Reassess mechanism diversity, falsifier calibration, sample-information limits, and available independent evidence classes before opening another strategy experiment; do not read this family’s reserved holdout, reopen quarantined families, or treat the three-date option archive as edge evidence. No paper/shadow/arm/live.

## Phase boundary

Executor evidence is partial. Grok 4.5 challenge, GPT 5.6 Sol finalization, learning/handoff reconciliation, deterministic staging/commit/integration/push, remote equality, and completion receipt remain required. No commit, push, merge, branch switch, broker action, or `RUN COMPLETE` claim occurred.

MOA_EXEC_DONE
