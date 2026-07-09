#!/usr/bin/env bash
# Paper scout tick: DNA-aware premium intents + paper ledger. No live.
set -euo pipefail
cd /Users/jarvis/dev/tsla-tsll-options-tracker
mkdir -p .cache/platform
{
  echo "=== paper_scout_tick $(date -u +%Y-%m-%dT%H:%M:%SZ) ==="
  .venv/bin/python -m trader_platform.autonomy_loop --mode paper --once
  echo "=== done ==="
} >> .cache/platform/paper_scout_cron.log 2>&1
exit 0
