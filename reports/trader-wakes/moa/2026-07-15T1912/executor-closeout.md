# MOA executor closeout — 2026-07-15T1912

WAKE: 2026-07-15T1912
PHASE: BUILD / L0 research only
ROLE: GPT 5.6 Sol executor / only writer
SESSION: off-hours; latest completed market data 2026-07-14
SLEEVE: $3,000
EXECUTOR STATUS: partial MOA phase complete; challenger/finalizer/integration pending; no `RUN COMPLETE` claim

## Strategy decision charter

ECONOMIC EDGE MECHANISM: downside volatility clusters. Inside a long-term SPY-and-symbol uptrend, refusing new bullish short-gamma exposure for five completed sessions after an underlying close loss of at least 3% should reduce the next ten-session 5% downside-barrier hazard.

CANDIDATE / FAMILY: `MULTINAME_NO_RECENT_DOWNSHOCK_PCS_21D_V1` / `noncollapse|recent_5d_downshock_exclusion|spy_and_symbol_sma100_uptrend|positive_60d_momentum|10_session_close_barrier_5pct|pcs_21d_2wide_planned` on SPY regime plus AAPL, MU, AMD, SMCI, TSLA, META, GOOGL, NVDA. TSLL was excluded because this non-collapse panel is non-levered. Current full-universe rank was context only; latest TSLL/TSLA/SMCI regimes were bearish, so this candidate's own rules imply stand-aside now.

CURRENT FUNNEL: `F0_MECHANISM`

EXACT WAKE DECISION: `BLOCKER_REMOVED_AND_RETESTED`. The prior epoch's mandatory three-no-advance burst stop was removed only by completing search-design reassessment, opening one successor direct-tail-hazard epoch, and exercising its smallest frozen train experiment. The dependent retest's terminal candidate disposition is `FAMILY_CLOSED`; it does not create a second wake outcome.

PREDECLARED FALSIFIER: close the exact family if chronological train had fewer than 120 eligible or 40 recent-shock episodes; fewer than 6 symbols in either group; eligible 5% close-barrier breach rate above 10%; control-minus-eligible breach edge below 5 percentage points; one-sided 90% circular-block-bootstrap edge lower bound non-positive; eligible worst-decile minimum return not milder; eligible mean terminal return after labeled 20 bps sensitivity non-positive; recent-five-session edge not larger than the stale six-to-ten-session placebo; or any chronology/overlap/source/strict-JSON/holdout/integrity failure.

DECISION CLOSED: reassessment blocker removed; exact candidate family closed at `F0_MECHANISM -> F0_MECHANISM_CLOSED` after failing the absolute non-collapse and timing-specificity gates. Holdout remains sealed.

## Complete Layered Edge Stack

- market / underlying: SPY regime plus fixed present-day AAPL, MU, AMD, SMCI, TSLA, META, GOOGL, NVDA panel; survivorship/listing-history biased, not a point-in-time universe
- forecast type: `non_collapse`
- economic mechanism: recent downside-shock clustering stand-aside within long-term equity uptrend
- option structure: future conditional one-lot put credit spread using nearest listed 18-24 DTE expiry; sell one 0.18-0.25 delta put, buy one same-expiry put exactly `$2` lower; require >=`$0.30` credit, positive bid on both legs, two-leg NBBO width <=`$0.20`, and no scheduled issuer earnings within five sessions; not priced at F0
- intended Greeks: positive delta, positive theta, short vega, bounded short gamma
- dangerous Greeks/risks: gap through the long wing, renewed shock clustering, vol/skew expansion, assignment/dividend risk, two-leg liquidity
- regime envelope: completed SPY and symbol closes above lag-safe prior-completed SMA100 and positive completed 60-session symbol return
- entry trigger: next session after completed signal close, with per-symbol outcome windows non-overlapping; eligible only when latest-five-session minimum completed daily return is greater than `-3%`
- exit / management: future option plan is 50% credit harvest, close after an underlying close 5% below entry, or ten-session time stop; the F0 experiment measures fixed ten-session close paths only
- capital fit: `capital_fit_usd=$200`; one-lot `max_loss_usd=$200` structural width bound before credit/closing friction; `max_lots=1`; one global correlated bullish portfolio-risk unit
- evidence / falsifier: date-disjoint 60%-target train versus outcome-unread holdout, direct close-barrier and worst-decile outcomes, circular-block uncertainty, stale-window specificity control, and the frozen gates above
- confidence stage: exact family closed at F0; no F1/F2/L1/capital-seat claim
- stand-aside: no entry below market/symbol trend anchors, with non-positive 60-session return, after a latest-five-session <=-3% loss, on source/integrity failure, or when a future quoted spread exceeds the structural one-lot bound
- mispricing claim: none; no IV, skew, credit, option-cost, or fill evidence

## Search-design reassessment

The previous epoch closed three consecutive post-advance wakes without strategy advancement:

1. breakout bull-call expression failed dual-cost and path-risk gates;
2. post-shock range compression failed pooled range/pin gates;
3. post-earnings signed continuation had negative absolute and paired expectancy despite a positive median.

These outcomes indicated that another nearby matched-control mean/pin study would repeat positive-middle/adverse-tail discovery. `docs/SEARCH_DESIGN_REASSESSMENT_2026-07-15T1912.md` opens `2026-07-15-tail-hazard-discovery`, where direct adverse-event probability and absolute downside quality precede option enthusiasm. `configs/search_epoch.json` records one completed no-advance wake in this successor epoch; pivot and burst-stop flags are false at streak 1.

## Dependent strategy retest

Evidence: `reports/trader-wakes/moa/2026-07-15T1912/downside-shock-stand-aside-train.json`

Provenance / chronology:

- split/dividend-adjusted yfinance closes, each persisted and SHA-256 hashed by the existing loader
- requested 2016-01-01 through end-exclusive 2026-07-15; common observed panel 2016-01-04 through 2026-07-14, 2,646 rows
- 1,115 frozen lag-safe, next-session-entry, non-overlapping blueprints
- train 703 blueprints through 2022-12-02; realized fraction 63.0493% because all symbols sharing a signal date stay on one side of the date-disjoint split
- untouched holdout 412 blueprints beginning 2022-12-09 through 2026-07-10; identity SHA-256 `acedd4c8cb0de2e0ee90f42c512af8885e730c78eb894f0a7f4eb8b34e223665`; outcomes unread
- train 548 eligible and 155 recent-shock episodes; all eight symbols in both groups; integrity violations `[]`; option-pricing calls `0`

Methodology limits retained by finalizer: the 5% endpoint uses daily closes only and can miss intraday lows; it is not an option mark, executable stop, or managed PCS result. Recent and stale shock flags can overlap, so their edge comparison is a confounded timing-specificity diagnostic rather than a pure alternative-mechanism RCT. The L0 uncertainty check separately circular-block resamples pooled groups, not multi-symbol dates, leaving residual dependence.

Train metrics:

- eligible 5% close-barrier breach rate: `0.27007299270072993`
- recent-shock breach rate: `0.3548387096774194`
- recent-shock breach-rate edge: `0.08476571697668944`
- one-sided 90% circular-block-bootstrap lower bound: `0.021356251471627063`
- eligible worst-decile minimum close return: `-0.13615073741962264`
- recent-shock worst-decile minimum close return: `-0.17832296567703598`
- eligible mean terminal return after labeled 20-bps sensitivity: `0.0094817259791593`
- stale-window placebo edge: `0.14572192513368987`

Passing gates: density, breadth, >=5pp relative edge, positive uncertainty lower bound, milder eligible tail, positive labeled-cost terminal mean, and zero integrity violations.

Failing gates:

1. absolute eligible breach rate `27.0073%` exceeded the frozen `10%` maximum;
2. stale six-to-ten-session shock edge `14.5722pp` exceeded the proposed recent-five-session edge `8.4766pp`.

Dominant failure mechanism: the rule separated relative risk but did not create a low-absolute-hazard population suitable for a one-lot bullish short-gamma candidate, and the stale placebo contradicted the claimed near-term clustering timing. Positive mean, tail, and uncertainty metrics cannot rescue those decision-critical failures.

Quarantine: do not rerun nearby 2%/4% shock cutoffs, 3/7-session windows, looser barrier thresholds, or a higher allowed breach rate. Reopen only with a new mechanism/evidence class. No holdout or option stage was spent.

## Search information versus strategy advancement

SEARCH INFORMATION: yes. The wake completed the mandatory burst-stop reassessment; added a reusable lag-safe downside-hazard/specificity lab; proved a date-disjoint outcome-unread holdout boundary; and decisively falsified one exact recent-shock PCS mechanism with non-vacuous 703-episode train evidence.

STRATEGY ADVANCEMENT: no. No candidate moved to F1, F2, F3, F4, L1, a capital seat, registry promotion, or paper intent. No living capital-seat leader exists.

## Validation

- strict TDD tracer bullets observed missing-module, unimplemented evaluator, unimplemented payload, and generic-failure-label failures before implementation
- focused behavioral/boundary/negative-control/integrity suite after complete-stack repair: `Ran 6 tests in 0.076s — OK`
- Python compile and CLI help smoke: exit `0`
- required final full suite after all executor surfaces: `.venv/bin/python -m unittest discover -s tests -p 'test_*.py'` -> `Ran 355 tests in 18.174s — OK`
- actual train retest after the date-disjoint split repair: exit `0`, `FAMILY_CLOSED`, 703 train / 412 untouched holdout
- current-code cache replay substantive equality excluding only `generated_at`: `True`; holdout identity remained `acedd4c8cb0de2e0ee90f42c512af8885e730c78eb894f0a7f4eb8b34e223665`
- income coverage refreshed: 21 structures / 246 hypotheses / 70 evolve artifacts / no living leader
- reusable lesson promoted by patching `options-strategy-analysis`: short-gamma discovery now requires direct adverse-event, absolute-hazard, tail, and mechanism-specificity gates before option pricing
- readiness phase/B checks unchanged; `reports/readiness/LATEST.md` intentionally not rewritten

## Freedom audit

Freedom preserved: the executor superseded the prior NEXT only after mandatory reassessment, chose a new multi-symbol direct-tail evidence class rather than TSLA/TSLL or recipe habit, made no allowlist change, and let the absolute-risk gates—not structure enthusiasm—close the family.

## Durable learning

A recent-downshock exclusion can create statistically positive relative hazard separation while remaining unusable for a small bullish short-gamma sleeve: absolute barrier frequency and timing-specificity controls must be primary, not post-hoc diagnostics. Keep the direct barrier/tail lab, but quarantine the exact timer.

## Exactly one next seed

Open new family key `LOW_DOWNSIDE_SEMIVARIANCE_ETF_BARRIER_HAZARD_F0`; freeze a cross-sectional low **downside-semivariance** rank (left-tail second moment, not plain HV) on lower-volatility liquid ETFs (SPY, QQQ, IWM, XLF, XLE, XLK, XLI, XLV), then test ten-session 5% close-barrier survival and worst-decile loss versus the high-downside-semivariance rank with multi-symbol date-blocked uncertainty and an untouched holdout. This is not a reopen or relabel of the closed low-HV mean-return family. Stop before option pricing unless the absolute <=10% breach gate passes.

## Partial-phase boundary

No commit, push, merge, deterministic integration, or `RUN COMPLETE` claim was made. Challenger and finalizer must critique the search-design reset, date-disjoint population, close-only barrier limitation, placebo interpretation, absolute gate, family quarantine, code/tests, and exactly-one-NEXT before integration.

MOA_EXEC_DONE
