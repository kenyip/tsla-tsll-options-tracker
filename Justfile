# Justfile - Easy commands for TSLA/TSLL Options Tracker
# Install just: https://github.com/casey/just

# One-time setup (works even if 'pip' is not in PATH)
setup:
    python -m pip install -r requirements.txt
    echo "Setup complete. Run 'just test' to run the strategy with tests"

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
