# Trader wake reports

Every self-evolution wake **must** leave residue here so Ken (and future Trader) can see what happened without digging Hermes session logs.

## Layout

```text
reports/trader-wakes/
  README.md                 # this file
  LATEST.md                 # copy of most recent wake (always overwrite)
  INDEX.md                  # newest-first index (append/update each wake)
  2026-07-09T0215-manual.md # one file per wake
```

## Required report shape

```markdown
# Trader wake — <ISO local time> — <manual|daily|weekly|...>

## Chose
One closed loop this wake.

## Did
- concrete actions

## Evidence
- paths, metrics, hyp IDs

## Durable changes
- files / hyps / skills / docs created or patched

## Next seed
What the next wake should do first.

## Gates
none | approval packet for Ken

## Runtime
- trigger: manual | cron daily | cron weekly
- duration / model notes if known
```

## How to read

```bash
just trader-wakes          # show LATEST + index head
just trader-wakes --all    # list all report files
open reports/trader-wakes/LATEST.md
```

Hermes cron output remains under `~/.hermes/profiles/trader/cron/output/` as a secondary transcript. **This folder is the human front door.**
