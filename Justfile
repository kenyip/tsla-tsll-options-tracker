# Justfile - Easy commands for TSLA/TSLL Options Tracker
# Install just: https://github.com/casey/just

# One-time setup
setup:
    pip install -r requirements.txt
    echo "Setup complete. Run 'just run' to launch dashboard"

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

# Note: 'backtest' recipe removed due to just parsing issues with multi-line python -c
# Use: python -c "from tsla_tsll_options_tracker import TSLA_TSLL_OptionsTracker; ..." directly if needed
