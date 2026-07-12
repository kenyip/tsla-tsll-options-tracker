#!/usr/bin/env bash
# Dual-pass trader wake: GPT 5.6 Sol executes (single writer) → Grok 4.5 challenges (read-only).
# Usage:
#   scripts/trader_wake_moa.sh                  # default: stress fit_3k SHIP set
#   scripts/trader_wake_moa.sh --goal "..."     # custom goal
#   scripts/trader_wake_moa.sh --executor-only
#   scripts/trader_wake_moa.sh --challenger-only --stamp 2026-07-09T2345
# Env overrides:
#   MOA_EXEC_PROVIDER / MOA_EXEC_MODEL (default openai-codex / gpt-5.6-sol)
#   MOA_CHALL_PROVIDER / MOA_CHALL_MODEL (default xai-oauth / grok-4.5)
#   MOA_MAX_TURNS_EXEC / MOA_MAX_TURNS_CHALL
# Note: Ken 2026-07-10 pin — Sol executor, Grok challenger.
#       Trader profile chat default may still be grok-4.5; MoA roles are independent.
set -euo pipefail

REPO="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO"

EXEC_PROVIDER="${MOA_EXEC_PROVIDER:-openai-codex}"
EXEC_MODEL="${MOA_EXEC_MODEL:-gpt-5.6-sol}"
CHALL_PROVIDER="${MOA_CHALL_PROVIDER:-xai-oauth}"
CHALL_MODEL="${MOA_CHALL_MODEL:-grok-4.5}"
MAX_EXEC="${MOA_MAX_TURNS_EXEC:-50}"
MAX_CHALL="${MOA_MAX_TURNS_CHALL:-30}"

GOAL=""
MODE="both"   # both | executor-only | challenger-only
STAMP=""
EXTRA_HYP_IDS="hyp_dna_tsll_put_credit_spread_b195f5fe,hyp_dna_amd_iron_condor_b3056133,hyp_dna_xom_call_credit_spread_77766a47"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --) shift ;; # ignore bare -- from `just recipe -- args`
    --goal) GOAL="$2"; shift 2 ;;
    --executor-only) MODE="executor-only"; shift ;;
    --challenger-only) MODE="challenger-only"; shift ;;
    --stamp) STAMP="$2"; shift 2 ;;
    --hyps) EXTRA_HYP_IDS="$2"; shift 2 ;;
    -h|--help)
      sed -n '2,16p' "$0"
      exit 0
      ;;
    *)
      echo "Unknown arg: $1" >&2
      exit 2
      ;;
  esac
done

if [[ -z "$STAMP" ]]; then
  STAMP="$(date +%Y-%m-%dT%H%M)"
fi
if [[ -z "$GOAL" ]]; then
  GOAL="Regime+cost stress and honest capital judgment on fit_3k defined-risk SHIP set: ${EXTRA_HYP_IDS}. No live. No new vanity evolve spam."
fi

MOA_DIR="reports/trader-wakes/moa/${STAMP}"
mkdir -p "$MOA_DIR"
PROMPT_DIR="$MOA_DIR/prompts"
mkdir -p "$PROMPT_DIR"

cat > "$MOA_DIR/meta.json" <<EOF
{
  "stamp": "$STAMP",
  "goal": $(python3 -c 'import json,sys; print(json.dumps(sys.argv[1]))' "$GOAL"),
  "mode": "$MODE",
  "executor": {"provider": "$EXEC_PROVIDER", "model": "$EXEC_MODEL"},
  "challenger": {"provider": "$CHALL_PROVIDER", "model": "$CHALL_MODEL"},
  "hyp_ids": $(python3 -c 'import json,sys; print(json.dumps(sys.argv[1].split(",")))' "$EXTRA_HYP_IDS"),
  "repo": "$REPO"
}
EOF

# --- Executor prompt (single writer to disk) ---
cat > "$PROMPT_DIR/01-executor.txt" <<EOF
MOA PHASE 1 — EXECUTOR (you are the ONLY writer).
You are Trader. Load skill trader-self-evolution.

PHASE: BUILD. Sleeve USD 3000. Paper/research only.
Model role: EXECUTOR (GPT 5.6 Sol). Do tool work. Mutate state once. Do not ask for a second agent.

GOAL:
$GOAL

HYP IDS (primary):
$EXTRA_HYP_IDS

REQUIRED LOOP (one closed loop):
1) Orient: reports/trader-wakes/LATEST.md, reports/readiness/LATEST.md, hyp registry notes for the three hyps.
2) Run regime stress:
   .venv/bin/python scripts/pcs_regime_stress.py \\
     --hyps "$EXTRA_HYP_IDS" \\
     --out .cache/platform/stress_regime_defined_risk.json
3) Run cost stress:
   .venv/bin/python scripts/pcs_cost_stress.py \\
     --hyps "$EXTRA_HYP_IDS" \\
     --out .cache/platform/stress_cost_defined_risk.json
4) Capital / rank judgment table for each hyp:
   - regime_hold, n_negative dense windows, worst window pnl
   - cost_hold, slip_5 verdict/pnl
   - capital_fit honesty
   - promote / hold / demote research_toy or needs_more_stress
5) Durable closeout ONLY under:
   - reports/trader-wakes/moa/${STAMP}/executor-closeout.md  (full MoA residue)
   - reports/trader-wakes/${STAMP}-moa-exec.md
   - Update reports/trader-wakes/LATEST.md with MoA-exec summary + NEXT SEED for challenger merge
   - Prepend reports/trader-wakes/INDEX.md
   - Update reports/readiness/LATEST.md stress rows / NEXT if evidence changed
6) Optional surgical hyp notes/evidence_links only if justified (prefer JSON evidence; avoid full yaml dump churn).

HARD STOPS:
- No live / broker login / agentic arm
- No status → shadow/live
- No second full free evolve pass (stress only)
- Do not invent metrics — cite JSON paths

Close with: MOA_EXEC_DONE and paths written.
EOF

# --- Challenger prompt (read-only critique) ---
cat > "$PROMPT_DIR/02-challenger.txt" <<EOF
MOA PHASE 2 — CHALLENGER (read-only judgment).
You are Trader critic. Load skill trader-self-evolution.

PHASE: BUILD. Sleeve USD 3000.
Model role: CHALLENGER (Grok 4.5). You do NOT re-run evolve, do NOT open broker, do NOT --apply evolve.
You MAY read files and run read-only \`jq\`/\`python -c\` to inspect JSON. Prefer no hyp yaml writes; if a capital_fit label is clearly wrong, note the surgical fix for merge — do not bulk-rewrite registry.

GOAL of original wake:
$GOAL

READ THESE FIRST (required):
- reports/trader-wakes/moa/${STAMP}/meta.json
- reports/trader-wakes/moa/${STAMP}/executor-closeout.md
- reports/trader-wakes/${STAMP}-moa-exec.md  (if present) or LATEST
- .cache/platform/stress_regime_defined_risk.json
- .cache/platform/stress_cost_defined_risk.json
- reports/readiness/LATEST.md

FIXED RUBRIC (score each hyp PASS/FAIL + one line why):
1. capital_fit honesty (fit_3k vs research_toy / open_risk conflict)
2. defined-risk preferred for \$3k (PCS/CCS/IC > naked)
3. falsification quality (regime + cost numbers present, not vibes)
4. no overclaim (SHIP ≠ live-ready; B6/B7 still separate)
5. next seed is ONE closed loop (not a menu)
6. no live/shadow promotion without gates

OUTPUT (write these files; nothing else durable unless rubric requires a tiny readiness NEXT patch):
1) reports/trader-wakes/moa/${STAMP}/challenger-critique.md
   Structure:
   - VERDICT_PER_HYP table
   - DISAGREEMENTS with executor (must cite evidence)
   - MERGE_ACTIONS: keep | demote | relabel | rewrite_next_seed
   - RUBRIC_SCORECARD
2) reports/trader-wakes/moa/${STAMP}/merged-next-seed.md  (single next seed after critique)
3) reports/trader-wakes/${STAMP}-moa-merge.md  (short human-facing merge)
4) Update reports/trader-wakes/LATEST.md to the merge summary (not re-running stress)
5) Prepend INDEX.md with moa-merge line
6) If NEXT on readiness is wrong after critique, patch readiness NEXT only

HARD STOPS:
- No evolve --apply
- No live
- No parallel hyp mass-create
- Challenge claims that lack JSON evidence

Close with: MOA_CHALL_DONE and paths written.
EOF

run_exec() {
  echo "=== MoA EXECUTOR: $EXEC_PROVIDER / $EXEC_MODEL ==="
  set +e
  hermes -p trader chat \
    -q "$(cat "$PROMPT_DIR/01-executor.txt")" \
    --provider "$EXEC_PROVIDER" \
    -m "$EXEC_MODEL" \
    --max-turns "$MAX_EXEC" \
    2>&1 | tee "$MOA_DIR/executor-session.log"
  ec=${PIPESTATUS[0]}
  set -e
  echo "$ec" > "$MOA_DIR/executor-exit.txt"
  if [[ $ec -ne 0 ]]; then
    echo "WARN: executor exit $ec — challenger may still review partial residue" >&2
  fi
}

run_chall() {
  if [[ ! -f "$MOA_DIR/executor-closeout.md" ]] && [[ ! -f "reports/trader-wakes/${STAMP}-moa-exec.md" ]]; then
    echo "ERROR: no executor closeout found under $MOA_DIR or ${STAMP}-moa-exec.md" >&2
    echo "Run executor first or pass a stamp that has residue." >&2
    exit 1
  fi
  echo "=== MoA CHALLENGER: $CHALL_PROVIDER / $CHALL_MODEL ==="
  set +e
  hermes -p trader chat \
    -q "$(cat "$PROMPT_DIR/02-challenger.txt")" \
    --provider "$CHALL_PROVIDER" \
    -m "$CHALL_MODEL" \
    --max-turns "$MAX_CHALL" \
    2>&1 | tee "$MOA_DIR/challenger-session.log"
  ec=${PIPESTATUS[0]}
  set -e
  echo "$ec" > "$MOA_DIR/challenger-exit.txt"
  return "$ec"
}

case "$MODE" in
  both)
    run_exec
    run_chall || true
    ;;
  executor-only)
    run_exec
    ;;
  challenger-only)
    run_chall
    ;;
esac

echo
echo "=== MoA complete ==="
echo "stamp:  $STAMP"
echo "dir:    $REPO/$MOA_DIR"
echo "meta:   $MOA_DIR/meta.json"
ls -la "$MOA_DIR" || true
echo "Front door: just trader-wakes"
echo "MoA dir:    just trader-wake-moa -- (already ran) or ls reports/trader-wakes/moa/"
