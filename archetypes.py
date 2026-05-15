"""v1.10 — named StrategyConfig presets for the archetype bake-off.

An "archetype" is a coherent (entry × risk × exit × roll-policy) tuple. The
bake-off runs every archetype × ticker through the standard validation gauntlet
(5y backtest + 12-regime suite + walk-forward static OOS) and ranks them on the
group-level + capital-time metrics added in backtest.py v1.10.

The point is to test very different strategy shapes against each other rather
than tuning one shape. The shape that wins per ticker becomes the new baseline
for re-deriving adaptive rules — the existing fleet of 5 rules was found under
the HoldToDecay archetype's trade log and does not transfer.

All non-control archetypes ship with adaptive_rules=() intentionally. Rules
must be re-derived from the winning archetype's output (analyze.py) before any
get shipped.
"""

from strategies import StrategyConfig, get_config


# Control — current v1.13 shipping config per ticker. Pulled from
# DEFAULT_CONFIG_BY_TICKER via get_config so it tracks any further tuning.
HOLD_TO_DECAY = {
    'TSLA': get_config('TSLA'),
    'TSLL': get_config('TSLL'),
}

# QuickHarvest — exit-driven archetype: small profit fast, tight stop, allow
# one roll to recover the rare adverse setup. Directly tests "every group
# positive" hypothesis: profit_target=18% means most groups close green inside
# 1–2 bars; max_loss=1.2× + roll catches the bad starts.
QUICK_HARVEST = {
    'TSLA': StrategyConfig(
        ticker='TSLA',
        long_dte=2, long_target_delta=0.35,
        bear_dte=2, bear_target_delta=0.35,
        min_credit_pct=0.020,
        profit_target=0.18,
        max_loss_mult=1.2,
        delta_breach=0.55,
        daily_capture_mult_short=5.0,
        regime_flip_exit_enabled=False,
        roll_on_max_loss=True, roll_dte=5, roll_target_delta=0.25, roll_credit_ratio=1.0,
        max_rolls_per_group=1, max_chain_loss_mult=1.5,
        adaptive_rules=(),
    ),
    'TSLL': StrategyConfig(
        ticker='TSLL',
        long_dte=1, long_target_delta=0.35,
        bear_dte=2, bear_target_delta=0.30,
        min_credit_pct=0.025,
        profit_target=0.18,
        max_loss_mult=1.2,
        delta_breach=0.50,
        daily_capture_mult_short=5.0,
        regime_flip_exit_enabled=True,
        roll_on_max_loss=True, roll_dte=3, roll_target_delta=0.25, roll_credit_ratio=1.0,
        max_rolls_per_group=1, max_chain_loss_mult=1.5,
        adaptive_rules=(),
    ),
}

# PremiumSlow — opposite end: longer DTE, lower delta, wider tolerance, two
# rolls of management. Closest to the original v1.1 shape; tests whether
# slower theta capture with bigger rolling cushion wins back what shorter DTE
# beats it by per-contract.
PREMIUM_SLOW = {
    'TSLA': StrategyConfig(
        ticker='TSLA',
        long_dte=21, long_target_delta=0.15,
        bear_dte=14, bear_target_delta=0.15,
        min_credit_pct=0.006,
        profit_target=0.50,
        max_loss_mult=2.5,
        delta_breach=0.40,
        dte_stop=7, dte_stop_min_entry=14,
        daily_capture_mult_short=1.5, daily_capture_mult_mid=1.5, daily_capture_mult_long=1.0,
        regime_flip_exit_enabled=False,
        roll_on_max_loss=True, roll_dte=21, roll_target_delta=0.12, roll_credit_ratio=1.0,
        max_rolls_per_group=2, max_chain_loss_mult=2.0,
        adaptive_rules=(),
    ),
    'TSLL': StrategyConfig(
        ticker='TSLL',
        long_dte=14, long_target_delta=0.15,
        bear_dte=10, bear_target_delta=0.15,
        min_credit_pct=0.006,
        profit_target=0.50,
        max_loss_mult=2.5,
        delta_breach=0.40,
        dte_stop=5, dte_stop_min_entry=10,
        daily_capture_mult_short=1.5, daily_capture_mult_mid=1.5, daily_capture_mult_long=1.0,
        regime_flip_exit_enabled=True,
        roll_on_max_loss=True, roll_dte=14, roll_target_delta=0.12, roll_credit_ratio=1.0,
        max_rolls_per_group=2, max_chain_loss_mult=2.0,
        adaptive_rules=(),
    ),
}

# ReversalScalp — 1-DTE high-delta, no rolling. The "close EOD" archetype
# under daily-bar granularity. profit_target=10% + max_loss=1.0× = take any
# small win, hard-stop on any adverse move. No chain management — every trade
# stands alone.
REVERSAL_SCALP = {
    'TSLA': StrategyConfig(
        ticker='TSLA',
        long_dte=1, long_target_delta=0.40,
        bear_dte=1, bear_target_delta=0.40,
        min_credit_pct=0.020,
        profit_target=0.10,
        max_loss_mult=1.0,
        delta_breach=0.60,
        daily_capture_mult_short=10.0,
        regime_flip_exit_enabled=False,
        roll_on_max_loss=False,
        max_rolls_per_group=0,
        adaptive_rules=(),
    ),
    'TSLL': StrategyConfig(
        ticker='TSLL',
        long_dte=1, long_target_delta=0.40,
        bear_dte=1, bear_target_delta=0.40,
        min_credit_pct=0.020,
        profit_target=0.10,
        max_loss_mult=1.0,
        delta_breach=0.60,
        daily_capture_mult_short=10.0,
        regime_flip_exit_enabled=True,
        roll_on_max_loss=False,
        max_rolls_per_group=0,
        adaptive_rules=(),
    ),
}


ARCHETYPES = {
    'HoldToDecay':   HOLD_TO_DECAY,
    'QuickHarvest':  QUICK_HARVEST,
    'PremiumSlow':   PREMIUM_SLOW,
    'ReversalScalp': REVERSAL_SCALP,
}
