# Merged NEXT SEED — 2026-07-11T1842

**Keep (tightened for capture reality):**

Implement append-safe RTH capture of **all available expirations** into the normalized option-quote archive (current path defaults to first expiry and overwrites a single CSV), accumulate **at least three distinct market dates**, then run provider-backed historical entry / coverage restress.

**Hard constraint:** do **not** free-evolve proxy DNA while observed date coverage remains one market date.

**Out of scope this seed:** capital path, shadow, live, L1 claims, retuning cost-fragile proxies.

**Success when:** archive shows ≥3 NY market dates with multi-expiry observed rows; provider coverage counters report multi-date covered requests; any provider-backed historical sim either produces honest trade-leg coverage or fail-closed reject — without inventing L1 from synthetic marks alone.
