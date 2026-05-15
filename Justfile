# Justfile - Easy commands for TSLA/TSLL Options Tracker

venv_dir := ".venv"
py       := venv_dir / "bin" / "python"
streamlit := venv_dir / "bin" / "streamlit"

# Show available commands
default:
    @just --list

# One-time setup: create venv and install dependencies
setup:
    #!/usr/bin/env bash
    set -euo pipefail

    # Pick a working python interpreter for bootstrapping
    if command -v python3 >/dev/null 2>&1; then
        BOOT_PY=python3
    elif command -v python >/dev/null 2>&1; then
        BOOT_PY=python
    else
        echo "Error: no 'python3' or 'python' found on PATH." >&2
        echo "Install Python 3.10+ first (e.g. 'sudo pacman -S python' on Arch)." >&2
        exit 1
    fi

    # Create the venv if it isn't there yet (prefer uv when available)
    if [ ! -x "{{py}}" ]; then
        echo "Creating virtual environment in {{venv_dir}}/ ..."
        if command -v uv >/dev/null 2>&1; then
            uv venv "{{venv_dir}}"
        else
            if ! "$BOOT_PY" -m venv "{{venv_dir}}"; then
                echo "" >&2
                echo "Failed to create venv. If you're on Debian/Ubuntu, run:" >&2
                echo "    sudo apt install python3-venv" >&2
                echo "Then re-run 'just setup'." >&2
                exit 1
            fi
        fi
    fi

    echo "Installing dependencies into {{venv_dir}} ..."
    if command -v uv >/dev/null 2>&1; then
        uv pip install --python "{{py}}" -r requirements.txt
    else
        "{{py}}" -m ensurepip --upgrade >/dev/null 2>&1 || true
        "{{py}}" -m pip install --upgrade pip
        "{{py}}" -m pip install -r requirements.txt
    fi

    echo ""
    echo "Setup complete. Try:  just test   or   just run"

# Today's live recommendation (uses the same engine code as the backtest)
test:
    {{py}} live.py

# Launch the Streamlit dashboard
run:
    {{streamlit}} run tsla_options_dashboard.py

# Detailed last 2 weeks trade log
recent-trades:
    {{py}} recent_performance.py

# Run baseline backtest on TSLA + TSLL
backtest *ARGS:
    {{py}} run_backtest.py {{ARGS}}

# Run strategy against canonical regime suite (huge_down, normal_down, flat, ...)
# Use BEFORE and AFTER every strategy tweak per CLAUDE.md
scenarios *ARGS:
    {{py}} run_scenarios.py {{ARGS}}

# Re-curate canonical scenario windows (after data drifts substantially)
scenarios-discover:
    {{py}} scenarios.py --discover

# Walk-forward optimization over StrategyConfig knobs
optimize *ARGS:
    {{py}} optimize.py {{ARGS}}

# Sweep a single StrategyConfig knob and report per-ticker P/L, DD, suite, score.
# Examples:
#   just sweep max_loss_mult --values 1.2,1.5,1.8,2.5
#   just sweep delta_breach --values 0.30,0.40,0.50,0.60 --tickers TSLA
#   just sweep long_dte --values 3,7,14 --vs long_target_delta --vs-values 0.15,0.20,0.30
sweep *ARGS:
    {{py}} sweep.py {{ARGS}}

# Run feature-importance analysis and emit candidate adaptive-rule sketches.
# This is the v1.12 automated rule-proposer for the critic loop.
# Examples:
#   just analyze
#   just analyze --tickers TSLL --top 5
#   just analyze --features iv_rank,ret_14d,ema_stack
analyze *ARGS:
    {{py}} analyze.py {{ARGS}}

# v1.14 archetype bake-off — head-to-head comparison of strategy archetypes
# (HoldToDecay / QuickHarvest / PremiumSlow / ReversalScalp) across 5y + suite + OOS.
bakeoff *ARGS:
    {{py}} archetype_bakeoff.py {{ARGS}}

# Active-position tracker: status of open positions (`positions.yaml`)
# `just positions`             — status of all open positions
# `just positions add TSLA put 385 2026-05-08 2026-05-15 4.40`
# `just positions close TSLA 385`
# `just positions example`     — write a sample positions.yaml
positions *ARGS:
    {{py}} manage_positions.py {{ARGS}}

# Clean generated plots
clean:
    rm -f *.png
    echo "Cleaned generated files"
