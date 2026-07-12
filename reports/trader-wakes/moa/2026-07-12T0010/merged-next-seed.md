# Merged NEXT SEED — 2026-07-12T0010

**Authoritative for next BUILD wake.**

## Decision retained from executor

- Shared-position PCS/CCS/IC **router family stays REJECT** this cycle.
- Do **not** retune credit floors / DNA on the router to chase CCS/IC accept rates after cost/DD rejection.
- Funnel diagnostic is **done** (selected → accepted → reject_reason; CCS/IC selected broadly, credit-floor rejects dominate).

## ONE NEXT SEED

Leave the router. Build a minimal paper-only **collared covered-call** simulator:

1. Structure: 100 shares + long protective put + short call
2. Capital honesty first:
   - `capital_fit_usd` = full 100-share notional (+ net option debit if any)
   - 1-lot `max_loss_usd` = downside floor net of option premia; explicit `max_lots`
   - Eligible symbols: liquid **non-levered** names with `spot*100 ≤ 3000`
   - If fewer than two current universe members qualify, expand `universe.yaml` with 3–5 liquid sub-$30 optionable names **or** fail the class closed this cycle — **do not** default to TSLL share-hold
3. Loop hygiene: no-close-bar re-entry; label dividends/assignment/early-exercise limitations
4. Immediate falsify (no registry SHIP-first):
   - 5% adverse leg slip
   - $0.01 fixed half-spread per option leg
   - Absolute gates: non-vacuous after-cost SHIP, max loss ≤$300, window max DD ≤$75, dense-neg ≤5
5. Reject the class unless gates clear; no capital seat; no live/shadow/agentic

## Parallel (not the BUILD seed)

RTH: next distinct NY market date → append all-expiration TSLL archive 1→2/3. No provider-backed historical simulation before 3/3.

## Hard stops

Paper/research only. No evolve promote to shadow/live. No broker. No arm.
