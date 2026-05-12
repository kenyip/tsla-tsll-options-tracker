# Justfile - Easy commands for TSLA/TSLL Options Tracker
# Install just: https://github.com/casey/just

# One-time setup
setup:
    pip install -r requirements.txt
    echo "✅ Setup complete. Run 'just run' to launch dashboard"

# Launch the Streamlit dashboard
run:
    streamlit run tsla_options_dashboard.py

# Quick backtest on recent synthetic data (last ~20 trading days)
backtest:
    python -c "
from tsla_tsll_options_tracker import TSLA_TSLL_OptionsTracker
tracker = TSLA_TSLL_OptionsTracker(starting_capital=250000)
tracker.load_or_generate_historical('TSLA', periods=400)
print('\n=== TSLA Recent Performance Backtest (last 20 days) ===')
tracker.backtest_premium_selling('TSLA', start_idx=380)
print('\n=== TSLL Recent Performance Backtest (last 20 days) ===')
tracker.backtest_premium_selling('TSLL', start_idx=380)
"

# Detailed last 2 weeks trade log (entry, management, exit, P/L)
recent-trades:
    python recent_performance.py

# Walk-forward optimization (find better parameters without future knowledge)
optimize:
    python walk_forward_optimizer.py

# Clean generated plots
clean:
    rm -f *.png
    echo "Cleaned generated files"