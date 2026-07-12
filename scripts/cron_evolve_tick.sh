#!/usr/bin/env bash
# Free strategy DNA evolve: catalog × symbols → sim → candidate hyps. No live. No code edits.
set -euo pipefail
cd /Users/jarvis/dev/tsla-tsll-options-tracker
mkdir -p .cache/platform
{
  echo "=== evolve_tick $(date -u +%Y-%m-%dT%H:%M:%SZ) ==="
  .venv/bin/python -m trader_platform.evolve_tick --once --apply \
    --top-symbols 4 --mutants 1 --max-population 20 --max-create 5 \
    --sleeve-usd 3000
  echo "=== done ==="
} >> .cache/platform/evolve_cron.log 2>&1
exit 0
