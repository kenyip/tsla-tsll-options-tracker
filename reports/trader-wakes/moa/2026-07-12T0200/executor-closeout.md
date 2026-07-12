# MOA BUILD lab executor closeout — 2026-07-12T0200

WAKE: 2026-07-12T0200 PDT (Sunday; market closed)
PHASE: BUILD
SLEEVE: 3000 USD
ROLE: GPT 5.6 Sol executor / only writer
PAPER_ONLY: true

## Chosen loop

P3 quality falsify: test whether tighter, premium-financed collars on non-levered sub-$30 names can turn the new collar scaffold into a dense, positive after-cost candidate without breaching the absolute $3k sleeve gates.

Hypothesis: tighter protective puts plus lower-delta covered calls can finance protection enough to produce dense positive after-cost collars with 1-lot max loss <=$300 and window max drawdown <=$75.

Falsifier: no exact DNA passes both 5% slip and $0.01-per-leg axes with n>=8, positive PnL, max loss <=$300, window max DD <=$75, dense-negative windows <=5, and independent ledger integrity.

Why this superseded NEXT's open choice: the scaffold existed but its first run did not search the management surface. One bounded exact grid could either find a paper-testable row or close the family without more proxy polishing.

## Validity prerequisites checked

- No-future semantics: `data.build` row-t features only; simulator acts on the current row.
- Population purity: 1,152/1,152 rows are `collared_covered_call`; eight explicitly non-levered sub-$30 names.
- Capital honesty: every entry uses 100-share notional plus positive option debit; every tested row remained <=$300 worst-case 1-lot loss and `max_lots=1`.
- Cost semantics: exact DNA rerun separately at 5% adverse option-leg slip and $0.01 adverse half-spread per option leg.
- Behavioral controls: independent trade-ledger PnL recomputation and no-close-bar-reentry audit on both axes for every row.
- Claim boundary: BS proxy with synthetic strikes/expiries; no observed option surface, dividends, or assignment. Discovery/falsification only; no L1 or promotion claim.

## Blocking flaw repaired

`evaluate_collar_absolute_gates()` previously omitted positive after-cost PnL, so a dense losing row could pass if its loss and drawdown were small. The gate now explicitly rejects `total_pnl_per_contract <= 0`; a behavioral boundary test proves a dense -$0.01 result cannot pass.

Evidence:
- `trader_platform/research/collar_sim.py`
- `tests/test_collar_sim.py` — 12/12 pass

## Experiment

Artifact: `.cache/platform/collar_management_grid_2026-07-12T0200.json`

Grid:
- Symbols: F, SOFI, AAL, PFE, SNAP, NIO, CCL, SMCI
- DTE: 7, 14, 21, 30
- Put delta: 0.25, 0.35, 0.40
- Call delta: 0.10, 0.20, 0.30
- Profit target: 0.25, 0.40
- Defined-loss exit fraction: 0.35, 0.70
- 144 exact configs per symbol; 1,152 rows total; two cost reruns per row

## Result and decision

Decision: **REJECT_COLLAR_MANAGEMENT_GRID_THIS_CYCLE**.

- Cost-axis passes: **0 / 1,152**
- Integrity failures: **0 / 1,152**
- Rows positive on both cost axes: **258 / 1,152**
- Rows with worst max loss <=$300 on both axes: **1,152 / 1,152**
- Rows with worst-axis window max DD <=$75: **0 / 1,152**
- Tightest worst-axis DD: SMCI, 30 DTE / put delta .25 / call delta .30 / PT .25 / loss .35, **$142.48** (5% axis n44 / +$808.97; fixed-$ axis n47 / +$1,284.60; max loss $298.75/$299.97)
- F, PFE, SNAP, and NIO had no row positive on both cost axes.
- SOFI/AAL/CCL produced some positive cost rows but their best risk paths still had window DD roughly $235.53 / $183.03 / $357.52 or worse.

The family can produce proxy profit, but not competitive path risk under the explicit absolute gate. No hypothesis registered, no status changed, and no capital seat created.

## Durable residue

- New reusable exact grid: `scripts/collar_management_grid.py`
- Gate fix and boundary test prevent losing rows from passing collar reject-unless.
- Coverage/doctrine now records the 1,152-row rejection rather than leaving a collar-retune invitation.
- No living quality leader; formal B checks unchanged; phase remains BUILD / L0.

## Freedom audit

No prompt rule blocked a higher-information valid experiment. The main tooling constraint is the absent historical observed option surface; it narrows this result to proxy-family falsification but did not block the chosen management-risk question.

## ONE NEXT SEED

Re-run the historical BAC Friday 7-DTE / $1 PCS transient under the **current** listed-Friday/actual-DTE simulator with exact B3, 5% slip, $0.01-per-leg fixed cost, independent ledger checks, and the current no-leader absolute gates (after-cost positive, max loss <=$300, window DD <=$75, dense-negative <=5). Its old $69.64 DD result predates the listed-expiry correction and is context only; either establish a fresh living leader or reject it.

## Score

Progress type: P3 quality falsify + validity repair
Score: **4/5**
Honesty: **L0 BUILD** — no L1 candidate, no real-account readiness

GATES: none
MOA_EXEC_DONE
