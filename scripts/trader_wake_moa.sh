#!/usr/bin/env bash
# Compatibility entrypoint for a named stress/judgment MoA wake.
# All execution is delegated to the contract-v2 BUILD orchestrator so this
# entrypoint cannot bypass clean preflight, finalization, learning promotion,
# commit/push/main integration, or postflight verification.
set -euo pipefail

REPO="$(cd "$(dirname "$0")/.." && pwd)"
BUILD_WRAPPER="$REPO/scripts/trader_build_lab_moa.sh"

GOAL=""
STAMP=""
MODE_FLAG=""
EXTRA_HYP_IDS="hyp_dna_tsll_put_credit_spread_b195f5fe,hyp_dna_amd_iron_condor_b3056133,hyp_dna_xom_call_credit_spread_77766a47"

usage() {
  cat <<'EOF'
Usage: scripts/trader_wake_moa.sh [--goal TEXT] [--hyps CSV] [--stamp STAMP]
                                  [--executor-only|--challenger-only|--finalizer-only|--resume]

This compatibility adapter routes stress/judgment MoA work through
trader_build_lab_moa.sh and its deterministic completion contract.
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --) shift ;;
    --goal) GOAL="$2"; shift 2 ;;
    --hyps) EXTRA_HYP_IDS="$2"; shift 2 ;;
    --stamp) STAMP="$2"; shift 2 ;;
    --executor-only|--challenger-only|--finalizer-only|--resume)
      MODE_FLAG="$1"; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown arg: $1" >&2; usage >&2; exit 2 ;;
  esac
done

[[ -x "$BUILD_WRAPPER" ]] || {
  echo "ERROR: missing BUILD completion orchestrator: $BUILD_WRAPPER" >&2
  exit 1
}

if [[ -z "$GOAL" ]]; then
  GOAL="Regime+cost stress and honest capital judgment on the fit_3k defined-risk SHIP set: ${EXTRA_HYP_IDS}. Run the regime and cost stress tools, challenge capital-fit/status labels, repair claim-invalidating defects, and leave one evidence-backed next seed. No vanity evolve spam, broker action, or live/shadow promotion."
fi

args=(--slot manual-stress --goal "$GOAL")
[[ -n "$STAMP" ]] && args+=(--stamp "$STAMP")
[[ -n "$MODE_FLAG" ]] && args+=("$MODE_FLAG")

exec "$BUILD_WRAPPER" "${args[@]}"
