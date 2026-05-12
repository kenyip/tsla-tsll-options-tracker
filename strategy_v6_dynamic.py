#!/usr/bin/env python3
"""
TSLA/TSLL Strategy v6.6 - With Safe Import
"""

try:
    from dynamic_parameter_engine import get_dynamic_params, run_tests
    HAS_TESTS = True
except ImportError:
    HAS_TESTS = False

def main():
    if HAS_TESTS:
        run_tests()
    
    current = {
        'iv_rank': 13,
        'recent_14d_return': 11.2,
        'intraday_return': -4.4,
        'volume_surge': 1.8,
        'bias': 'bullish'
    }
    
    tsla = get_dynamic_params(current, 'TSLA', 425)
    tsll = get_dynamic_params(current, 'TSLL', 14.5)
    
    print("="*95)
    print(f"TSLA ${425} | IV {13} | 14d +{11.2}% | Intraday {-4.4}%")
    print("="*95)
    print(f"TSLA: {tsla['direction']} {tsla['strike']} @ {tsla['delta']} delta | {tsla['dte']} DTE | {tsla['expiration']} | {tsla['size_note']}")
    print(f"TSLL: {tsll['direction']} {tsll['strike']} @ {tsll['delta']} delta | {tsll['dte']} DTE | {tsll['expiration']} | {tsll['size_note']}")
    if tsla.get('short_term_calls_active'):
        print("\n>>> SHORT-TERM CALL SELLING MODULE ACTIVE <<<")
    print("="*95)

if __name__ == "__main__":
    main()
