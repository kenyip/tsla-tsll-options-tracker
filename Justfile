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

# Run strategy with automated tests (recommended)
test:
    {{py}} strategy_v6_dynamic.py

# Launch the Streamlit dashboard
run:
    {{streamlit}} run tsla_options_dashboard.py

# Detailed last 2 weeks trade log
recent-trades:
    {{py}} recent_performance.py

# Walk-forward optimization
optimize:
    {{py}} walk_forward_optimizer.py

# Clean generated plots
clean:
    rm -f *.png
    echo "Cleaned generated files"
