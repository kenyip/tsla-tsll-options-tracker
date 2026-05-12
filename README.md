# TSLA & TSLL Options Premium Selling Tracker & Dashboard

Expert options selling system for **daily profits** with **long-term bullish edge** on TSLA fundamentals (AI, Robotaxi, Optimus, Energy).

## Features
- **Black-Scholes Engine**: Real-time pricing, full Greeks, Taylor-expansion daily decay estimates (time + price move + IV change).
- **Live Scanner**: Ranks best OTM puts/calls by theta yield, POP, and safe distance.
- **Portfolio Tracker**: Unrealized P/L, daily theta capture, position management.
- **What-If Decay Analyzer**: Sliders for tomorrow's price move & IV change → instant P/L prediction.
- **Backtester**: Walk-forward test with strict risk rules (69% win rate in synthetic high-vol data).
- **Improvement Loop**: Log feedback and get parameter tuning suggestions.

## Quick Start (Linux / Mac / Windows)

```bash
git clone https://github.com/kenyip/tsla-tsll-options-tracker.git
cd tsla-tsll-options-tracker

# Install dependencies
pip install -r requirements.txt

# Run the beautiful Streamlit dashboard
streamlit run tsla_options_dashboard.py
```

Open in browser at http://localhost:8501

## How to Use Daily
1. Update current price & IV in sidebar.
2. Click "Scan Best Trades" → pick top setups.
3. Add to portfolio.
4. Use What-If tab to see tomorrow's expected P/L from decay.
5. Close at 50% profit or when delta breaches 0.40.

## API
- **Free**: yfinance (built-in)
- **Recommended Upgrade**: Polygon.io for real-time options chains ($49/mo)

## Strategy Summary
Sell high-IV premium on TSLA/TSLL (target 0.20-0.28 delta, 21-45 DTE). Bullish bias on puts. Wheel if assigned. Long-term: accumulate shares cheaper while harvesting volatility.

Built with Grok xAI | May 2026

**Disclaimer**: Educational tool only. Options trading involves substantial risk of loss. Paper trade first.