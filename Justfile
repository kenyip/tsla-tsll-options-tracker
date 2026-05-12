# Justfile - Easy commands for TSLA/TSLL Options Tracker

# One-time setup (tries multiple Python versions)
setup:
    @python3 -m pip install -r requirements.txt 2>/dev/null || \
    @python -m pip install -r requirements.txt 2>/dev/null || \
    @echo "Could not auto-install. Please run manually:"
    @echo "  python3 -m ensurepip --upgrade && python3 -m pip install -r requirements.txt"

# Run strategy with automated tests (recommended)
test:
    python strategy_v6_dynamic.py

# Launch the Streamlit dashboard
run:
    streamlit run tsla_options_dashboard.py

# Detailed last 2 weeks trade log
recent-trades:
    python recent_performance.py

# Walk-forward optimization
optimize:
    python walk_forward_optimizer.py

# Clean generated plots
clean:
    rm -f *.png
    echo "Cleaned generated files"
