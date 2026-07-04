# TSLA Delivery-Day Conditional Playbook — Jul 1, 2026

## Book Context
- 8x TSLA Jun 2028 LEAPS (2x $410 @ $13k, 4x $400 @ $11,225, 1x $410 @ $10,800, 1x $410 @ $11,200)
- Spot: $425.30 (pre-delivery)
- All shorts closed; book is naked LEAPS awaiting delivery catalyst
- Cycle: Aug 21 2026 (51 DTE) shorts available
- Target: Sell 2–4 shorts on the delivery reaction, split core + income sleeves
- Max practical shorts: 4 (leaves 4 LEAPS as trim/roll buffer)

## IV Inflation Model During Spike
Current chain mids are STALE (pre-delivery calm). When TSLA spikes:
- Moderate spike (+5-8%): IV inflates to ~1.10x current
- Strong spike (+9-14%): IV inflates to ~1.20x current
- Blowout spike (+15%+): IV inflates to ~1.25-1.30x current before vol crush begins

Premiums to target are the INFLATED print prices — selling into IV expansion is the whole point.

## Modeled Premiums at Spike Levels (Aug 21, 51 DTE)

| TSLA Peak | IV Mult | $480C | $490C | $500C | $510C | $520C | $530C | $540C | $550C |
|-----------|---------|-------|-------|-------|-------|-------|-------|-------|-------|
| $440      | 1.10x   | $18.91| $16.60| $14.50| $12.70| $11.10| $9.65 | $8.35 | $7.20 |
| $450      | 1.10x   | —     | $19.76| $17.30| $15.20| $13.30| $11.65| $10.15| $8.80 |
| $460      | 1.10x   | —     | —     | $20.64| $18.20| $16.00| $14.10| $12.40| $10.85|
| $475      | 1.10x   | —     | —     | —     | —     | $20.89| $18.60| $16.50| $14.60|
| $500      | 1.10x   | —     | —     | —     | —     | —     | —     | $25.15| $22.50|
| $475      | 1.20x   | —     | —     | —     | —     | $22.78| $20.29| $18.00| $15.93|
| $500      | 1.20x   | —     | —     | —     | —     | —     | —     | $27.44| $24.55|

(These are modeled mids. Use limit orders at or slightly below mid for realistic fills.)

---

## SCENARIO 1: MISS (< 390K deliveries, QoQ decline)

**Market reaction:** -3% to -6% on day-0, possibly -8% over 3 days
**TSLA peak zone:** $400–$412 (may not spike at all; gap down likely)
**IV:** Stays flat or compresses slightly; no premium expansion opportunity

### Action: WAIT — DO NOT SELL SHORTS ON A MISS
- TSLA dropping toward $400 makes every short too close to LEAPS strikes
- $475C minimum income strike at $400 spot = +18.75% OTM, but premium collapses with IV crush
- Income sleeve math breaks: credit hawked at wider strikes is too thin to justify capping the book
- Let the dust settle. If TSLA stabilizes $410–$420 and IV stays elevated (2-3 days later), THEN evaluate income shorts at $475C–$480C for $11–$14 credit (post-spike IV residual)
- **If TSLA falls below $400:** wait for IV to settle; becomes a patience game. No shorts below $420 spot

### Limit orders: NONE — no entry on a miss day

---

## SCENARIO 2: INLINE (390K–440K, in-line with whisper)

**Market reaction:** +0% to +2% day-0, +1% to +3% 3-day
**TSLA peak zone:** $425–$440
**IV:** Slight uptick to ~1.05x; mild premium expansion

### Action: SELL INCOME SLEEVE ONLY — moderate premium, wait for better
- Spike is too mild to justify wide core shorts (they'd pay $5-8, not worth capping upside)
- Income sleeve: sell 2x Aug $480C at the spike peak

| Contract | Strike | Target Credit | $/Day | Delta Est. | Upside Room |
|----------|--------|---------------|-------|------------|-------------|
| 2x       | $480C  | $12.50–$14.00 | ~$24–$27/day | ~0.22 | +12.9% from $425 |

**Why $480C:** Passes $700 conservative-rip stress test for the income sleeve (spread width $70–$80 = 54–62% of LEAPS basis). At these premium levels ($12.50+), you're getting $24+/day which exceeds the $15/day/short target.

### If spike extends to $440+:
- STILL only income sleeve. Don't chase core shorts yet.
- Could step down to $475C for more income if TSLA holds $440+ for 2+ hours: 2x $475C @ $15.00+ target ($29+/day)
- But $480C is safer and still very good income

### If spike fades back to $425:
- Shorts sold at $440+ peak should be green immediately
- Hold; theta works in your favor
- If premium drops to 50% of credit within 14 days, harvest and wait for next catalyst

### Limit orders to place:
```
SELL -2 TSLA Aug21 480C @ $12.50 LMT (day order, GTC if post-market)
  — Place when TSLA prints $435+ (don't sell into the first 15 min; let initial rip establish)
  — If not filled and TSLA reaches $440, lower to $11.80
```

---

## SCENARIO 3: MILD BEAT (440K–470K, above consensus but not blowout)

**Market reaction:** +2% to +5% day-0, +3% to +8% 3-day
**TSLA peak zone:** $434–$446
**IV:** Inflates to 1.08–1.12x; good premium expansion

### Action: SELL BOTH SLEEVES — income + core
This is the sweet spot. Enough IV expansion to make wide shorts pay well, but not so much that you're chasing a moonshot.

**Income sleeve (2 contracts):**
| Contract | Strike | Target Credit | $/Day | Delta Est. | Upside Room |
|----------|--------|---------------|-------|------------|-------------|
| 2x       | $480C  | $14.00–$17.00 | ~$27–$33/day | ~0.20 | +12.9% from $425 |

**Core sleeve (1-2 contracts):**
| Contract | Strike | Target Credit | $/Day | Delta Est. | Upside Room |
|----------|--------|---------------|-------|------------|-------------|
| 1x       | $530C  | $9.65–$11.65  | ~$19–$23/day | ~0.11 | +24.6% from $425 |
| 1x       | $540C  | $8.35–$10.15  | ~$16–$20/day | ~0.09 | +27.0% from $425 |

**Preferred structure at TSLA $440 peak:**
- 2x Aug $480C @ $15.50 target credit (income)
- 1x Aug $530C @ $10.50 target credit (core-wide)
- 1x Aug $540C @ $9.00 target credit (core-wide)
- Total: 4 shorts, $50.50 total credit (~$990/day gross), covers all 8 LEAPS theta + income

**Why 4 shorts, not 2–3:**
At a mild beat, TSLA likely settles $430–$440 range. The shorts are 9–27% OTM. 4 shorts is within the "6 max" rule, leaves 4 LEAPS as buffer, and captures the IV expansion premium before it crushes.

### If spike extends to $450+:
- HOLD existing shorts — they're still well OTM
- Consider adding 1x $550C or $560C core short if premium reaches $8.00+ with TSLA $450+
- DO NOT step income sleeve closer — the $480Cs you already sold are the right strikes
- Ladder UP, never duplicate the same strike zone

### If spike fades back to $425–$430:
- Income sleeve ($480C) should be solidly green within days
- Core sleeve ($530C/$540C) will be very green — harvest at 50%+ if TSLA stays below $435 for 10+ days
- After core harvest, can reload core at $520C–$530C level once TSLA stabilizes

### Limit orders to place:
```
SELL -2 TSLA Aug21 480C @ $14.50 LMT GTC
  — Place when TSLA prints $435+
  — Adjust limit down to $13.50 if TSLA reaches $445+ and no fill

SELL -1 TSLA Aug21 530C @ $10.50 LMT GTC
  — Place when TSLA prints $438+
  — Core sleeve; this can sit for a day or two

SELL -1 TSLA Aug21 540C @ $9.00 LMT GTC
  — Place when TSLA prints $438+
  — Pair with the $530C; either fill is fine, both is preferred
```

---

## SCENARIO 4: STRONG BEAT (470K–500K, well above consensus, possible record)

**Market reaction:** +5% to +10% day-0, +8% to +15% 3-day
**TSLA peak zone:** $446–$468
**IV:** Inflates to 1.15–1.20x; significant premium expansion

### Action: SELL BOTH SLEEVES — GO BIG ON CORE, MODERATE INCOME
IV expansion is your friend. Wide shorts that pay $3–$5 normally will pay $7–$12 today. Lock in the fat premium on the rip.

**Income sleeve (2 contracts):**
| Contract | Strike | Target Credit | $/Day | Delta Est. | Upside Room |
|----------|--------|---------------|-------|------------|-------------|
| 2x       | $480C  | $16.00–$22.00 | ~$31–$43/day | ~0.18 | +12.9% |

At $450+ with 1.15x IV, $480C models ~$19.76. At 1.20x IV, even richer. Target $18+ credit.

**Core sleeve (2 contracts):**
| Contract | Strike | Target Credit | $/Day | Delta Est. | Upside Room |
|----------|--------|---------------|-------|------------|-------------|
| 1x       | $540C  | $12.40–$16.50 | ~$24–$32/day | ~0.08 | +27.0% |
| 1x       | $550C  | $10.85–$14.60 | ~$21–$29/day | ~0.06 | +29.3% |

**Preferred structure at TSLA $455 peak (1.15x IV):**
- 2x Aug $480C @ $18.50 target credit (income)
- 1x Aug $540C @ $14.00 target credit (core-wide)
- 1x Aug $550C @ $12.50 target credit (core-wide)
- Total: 4 shorts, $63.50 total credit (~$1,245/day gross)

**Alternative if TSLA spikes to $465+:**
- Income sleeve becomes riskier at $480; shift income strikes to $490C
- 2x Aug $490C @ $17.00 target (income, safer spread width from $410 LEAPS)
- 1x Aug $540C @ $15.00 target (core)
- 1x Aug $550C @ $13.00 target (core)

### If spike extends to $475+:
- HOLD all existing shorts — they're printing green marks
- Consider 1 more core short: $560C or $570C if premium reaches $7.50+
- MAX 5 shorts at this point; don't over-cover
- At $475+, spot/LEAPS-strike ratio approaches 1.16x — well below extreme-rip threshold (1.35x), but getting warmer

### If spike fades to $430–$440:
- Excellent — all shorts should be solidly green
- Income ($480C) decays fast; harvest at 50%+ profit within 10–14 days
- Core ($540C/$550C) are almost free money at that point; harvest at 60%+ after 14 days
- Reload income sleeve at $480C or $475C when TSLA settles

### Limit orders to place:
```
SELL -2 TSLA Aug21 480C @ $18.50 LMT GTC
  — If TSLA gaps to $445+, raise to $19.50
  — If TSLA reaches $460+, shift to: SELL -2 490C @ $17.00 LMT GTC instead

SELL -1 TSLA Aug21 540C @ $14.00 LMT GTC
  — Place when TSLA prints $450+
  — Raise to $15.00 if TSLA hits $460+

SELL -1 TSLA Aug21 550C @ $12.50 LMT GTC
  — Place when TSLA prints $450+
  — Raise to $13.50 if TSLA hits $460+
```

---

## SCENARIO 5: BLOWOUT (500K+ deliveries, record quarter, possible new vehicle launch catalyst)

**Market reaction:** +10% to +15% day-0, +15% to +30%+ 3-day
**TSLA peak zone:** $468–$490+ (day-0), potentially $500–$550+ (3-day)
**IV:** Inflates to 1.20–1.30x initially, then may start crushing on day-1/2

### Action: SELL CORE-WIDE FIRST, INCOME SECOND, LADDER AGGRESSIVELY
This is the scenario where IV expansion makes $520–$550 shorts pay double their normal rate. You sell into the rip, not after.

**CRITICAL: Sell in two waves, not all at once.**

### Wave 1 — Core wide shorts (place immediately when TSLA spikes above $450):
| Contract | Strike | Target Credit | $/Day | Delta Est. | Upside Room |
|----------|--------|---------------|-------|------------|-------------|
| 2x       | $540C  | $15.00–$18.00 | ~$29–$35/day | ~0.08 | +27.0% from $425 |
| 1x       | $550C  | $13.00–$16.00 | ~$25–$31/day | ~0.06 | +29.3% from $425 |

These are your core shorts. At 1.2x IV with TSLA $470+, these print $14+. Even if TSLA keeps ripping to $500, these are 8–10% OTM and manageable.

### Wave 2 — Income shorts (place when TSLA peaks and shows first sign of fading, or if TSLA stabilizes at $460+):
| Contract | Strike | Target Credit | $/Day | Delta Est. | Upside Room |
|----------|--------|---------------|-------|------------|-------------|
| 1x       | $490C  | $17.00–$22.00 | ~$33–$43/day | ~0.18 | +15.2% from $425 |

**Why only 1 income short on a blowout:**
TSLA at $470–$490 is approaching LEAPS extreme-rip territory (1.35x × $410 = $554 / 1.35x × $400 = $540). Selling 2 tight shorts here risks capping the thesis at the exact moment it's working. 1 income short captures the IV premium; the rest is core-wide or nothing.

**Alternative — pure core strategy (4 wide, 0 income):**
If TSLA hits $480+ and shows no sign of fading:
- 2x $540C @ $16.00 target
- 2x $550C @ $14.00 target
- 0x income shorts
- This preserves maximum upside while still printing ~$60 credit ($1,176/day)
- The whole book stays safe through $600+; naked 4 LEAPS above 1.35x threshold if TSLA hits $554+

### If spike extends to $500+ (3-day move):
- At $500, spot/LEAPS-strike = 1.22x ($410) to 1.25x ($400) — approaching extreme-rip zone
- Close the INCOME short ($490C) if it's within 5% of $500 — it will be ITM soon
- Close 1 core short ($540C) if TSLA reaches $520 — it becomes challenged
- Consider closing ALL shorts and running LEAPS naked if TSLA sustains $540+ (1.35x threshold for $400 LEAPS)
- **Remember:** at 1.35x the short caps the LEAPS. Close short, let LEAPS run.

### If spike fades to $440–$455:
- All shorts become extremely profitable
- Income $490C: harvest at 50%+ within 7–10 days
- Core $540C/$550C: harvest at 60%+ within 14 days
- Reload income sleeve at $480C–$490C when TSLA settles

### Limit orders to place:
```
=== WAVE 1: CORE SHORTS (place immediately when TSLA > $450) ===
SELL -2 TSLA Aug21 540C @ $15.00 LMT GTC
  — Raise to $16.50 if TSLA hits $470+
  — Raise to $18.00 if TSLA hits $485+

SELL -1 TSLA Aug21 550C @ $13.00 LMT GTC
  — Raise to $14.50 if TSLA hits $470+
  — Raise to $16.00 if TSLA hits $485+

=== WAVE 2: INCOME SHORT (place when TSLA peaks/fades from first spike) ===
SELL -1 TSLA Aug21 490C @ $18.00 LMT GTC
  — Only place once TSLA shows a $2-3 fade from peak (e.g., peaks at $475, fades to $472)
  — Or place if TSLA stabilizes at $460+ for 30+ minutes
  — Raise to $20.00 if TSLA re-tests $480+

=== IF TSLA > $500 (day-2/3 extension): ===
BUY TO CLOSE -1 TSLA Aug21 490C (market or limit at 80% of sold credit)
  — Income short becomes too challenged
CONSIDER: close 1x $540C as well
  — If TSLA > $520, close all core $540Cs

=== IF TSLA > $554 (1.35x $410 LEAPS): ===
CLOSE ALL SHORTS — go naked on LEAPS
  — The short caps your thesis at exactly the wrong time
```

---

## Quick Reference: Delivery_Number → Scenario → Strike Table

| Delivery | Scenario  | TSLA Peak | Income Strikes | Core Strikes | Total Shorts | Total Est. Credit |
|----------|-----------|-----------|----------------|--------------|-------------|-------------------|
| < 390K   | MISS      | $400–412  | NONE           | NONE         | 0           | $0                |
| 390–440K | INLINE    | $425–440  | 2x $480C       | NONE         | 2           | $25–$28           |
| 440–470K | MILD BEAT | $434–446  | 2x $480C       | 1x $530C + 1x $540C | 4   | $47–$52           |
| 470–500K | STRONG   | $446–468  | 2x $480C       | 1x $540C + 1x $550C | 4   | $58–$67           |
| 500K+    | BLOWOUT   | $468–490+ | 1x $490C       | 2x $540C + 1x $550C | 4   | $60–$70           |

---

## Post-Spike Management Rules (All Scenarios)

### If the short is working (TSLA fades/stabilizes below strike):
1. **50%+ profit → harvest** (buy back short, keep LEAPS)
2. **Premium clock**: if harvesting at 50% within 14 days, that's excellent income velocity
3. **After harvest → wait budget**: days_to_wait = harvest_profit / target_daily_income
   - Example: Sold $480C at $15.00, harvest at $7.50 = $750 profit. Target $15/day. Wait ~50 days… but that's the full cycle. Practically: reload when next catalyst or IV pop happens.
4. **Reload strikes**: same strikes or slightly higher if TSLA has drifted up

### If the short is challenged (TSLA approaches or exceeds short strike):
1. **Short still OTM, > 8% from strike → HOLD** (LEAPS gaining more than short losing)
2. **Short within 8% of strike → evaluate roll up** (gap-rip roll protocol)
3. **Short ITM, DTE > 21 → HOLD** (don't panic; position is net profitable)
4. **Short ITM, DTE ≤ 14 → FORCE CLOSE + roll up-and-out or close both**
5. **Spot > 1.35x LEAPS strike → close all shorts, run LEAPS naked**

### Core vs. Income sleeve-specific rules:
- **Income sleeve ($480–$490C):** If challenged, compute close-both P/L. If positive, close both and redeploy. If negative but > -$500/contract and core sleeve is up, hold and let theta work.
- **Core sleeve ($530–$550C):** These should almost never be challenged unless TSLA hits moon. If challenged, the whole book is deeply profitable. Roll up aggressively (spot +15-20%) or close short and go naked.

### Vol Crush Warning
Delivery-day IV expansion is temporary. Within 2-3 days, IV will start compressing back. This affects management:
- **Shorts sold into IV expansion have a tailwind** from vega decay as well as theta
- **Shorts sold AFTER the spike (chasing) have no vega tailwind** — pure theta play
- **Harvest faster on vol crush**: if IV drops 10%+ from sale and short is 40%+ profited, harvest immediately rather than waiting for 50%

---

## Specific Limit Order Cheat Sheet (Copy-Paste Ready)

### Scenario 2 (Inline, TSLA $435+):
```
SELL -2 TSLA 082122C480 @ 12.50 LMT DAY
```

### Scenario 3 (Mild Beat, TSLA $438+):
```
SELL -2 TSLA 082122C480 @ 14.50 LMT GTC
SELL -1 TSLA 082122C530 @ 10.50 LMT GTC
SELL -1 TSLA 082122C540 @ 9.00 LMT GTC
```

### Scenario 4 (Strong Beat, TSLA $450+):
```
SELL -2 TSLA 082122C480 @ 18.50 LMT GTC
SELL -1 TSLA 082122C540 @ 14.00 LMT GTC
SELL -1 TSLA 082122C550 @ 12.50 LMT GTC
```
(If TSLA $460+: swap $480C → $490C @ $17.00; raise core limits $1–$2)

### Scenario 5 (Blowout, TSLA $470+):
```
=== WAVE 1 (immediate) ===
SELL -2 TSLA 082122C540 @ 15.00 LMT GTC
SELL -1 TSLA 082122C550 @ 13.00 LMT GTC

=== WAVE 2 (after peak/fade signal) ===
SELL -1 TSLA 082122C490 @ 18.00 LMT GTC
```
(If TSLA $485+: raise core limits $2–$3; if TSLA $500+: close income, consider closing all)

---

## Historical Delivery Reactions Reference (2019–2026)

| Percentile | Day-0 High | 3-Day High |
|------------|-----------|------------|
| p50 (median)| +2.1%    | +5.3%      |
| p75        | +4.3%    | +8.6%      |
| p90        | +7.2%    | +14.6%     |
| max        | +13.7%   | +32.4%     |

From $425.30 spot:
- p50 day-0: $434 (Scenario 3 — Mild Beat zone)
- p75 day-0: $444 (Scenario 3–4 boundary)
- p90 day-0: $456 (Scenario 4 — Strong Beat zone)
- p75 3-day: $462 (Scenario 4–5 boundary)
- p90 3-day: $487 (Scenario 5 — Blowout zone)

**The p90 3-day high lands exactly in the blowout scenario. This is a ~10% probability event, but it's the one that requires the most discipline (selling core-wide early, not chasing tight shorts late).**
