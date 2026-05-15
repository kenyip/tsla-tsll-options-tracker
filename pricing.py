#!/usr/bin/env python3
"""
Black-Scholes option pricing, greeks, and strike-from-delta solver.

Conventions:
- T is time to expiration in years (use DTE / 365.0)
- sigma is annualised volatility as a decimal (0.40 = 40%)
- r is the continuously-compounded risk-free rate
- q is the continuous dividend yield (0 for TSLA/TSLL)
- option_type is 'call' or 'put'

All greeks returned in "per 1 unit" form:
- delta: dV/dS                    (range [-1, 1])
- gamma: d2V/dS2                  (per $1 of underlying)
- theta: dV/dt PER YEAR           (divide by 365 for per-day)
- vega:  dV/dsigma PER 1.0 of vol (divide by 100 for per-vol-point)
- rho:   dV/dr PER 1.0 of rate
"""

from dataclasses import dataclass
from math import log, sqrt, exp
from scipy.stats import norm


SQRT_2PI = sqrt(2.0 * 3.141592653589793)


def _d1_d2(S, K, T, sigma, r=0.04, q=0.0):
    if T <= 0 or sigma <= 0:
        raise ValueError(f"T and sigma must be positive (T={T}, sigma={sigma})")
    vol_t = sigma * sqrt(T)
    d1 = (log(S / K) + (r - q + 0.5 * sigma * sigma) * T) / vol_t
    d2 = d1 - vol_t
    return d1, d2


def price(S, K, T, sigma, option_type, r=0.04, q=0.0):
    d1, d2 = _d1_d2(S, K, T, sigma, r, q)
    if option_type == 'call':
        return S * exp(-q * T) * norm.cdf(d1) - K * exp(-r * T) * norm.cdf(d2)
    return K * exp(-r * T) * norm.cdf(-d2) - S * exp(-q * T) * norm.cdf(-d1)


def delta(S, K, T, sigma, option_type, r=0.04, q=0.0):
    d1, _ = _d1_d2(S, K, T, sigma, r, q)
    if option_type == 'call':
        return exp(-q * T) * norm.cdf(d1)
    return -exp(-q * T) * norm.cdf(-d1)


def gamma(S, K, T, sigma, r=0.04, q=0.0):
    d1, _ = _d1_d2(S, K, T, sigma, r, q)
    return exp(-q * T) * norm.pdf(d1) / (S * sigma * sqrt(T))


def theta(S, K, T, sigma, option_type, r=0.04, q=0.0):
    d1, d2 = _d1_d2(S, K, T, sigma, r, q)
    common = -S * norm.pdf(d1) * sigma * exp(-q * T) / (2 * sqrt(T))
    if option_type == 'call':
        return common - r * K * exp(-r * T) * norm.cdf(d2) + q * S * exp(-q * T) * norm.cdf(d1)
    return common + r * K * exp(-r * T) * norm.cdf(-d2) - q * S * exp(-q * T) * norm.cdf(-d1)


def vega(S, K, T, sigma, r=0.04, q=0.0):
    d1, _ = _d1_d2(S, K, T, sigma, r, q)
    return S * exp(-q * T) * norm.pdf(d1) * sqrt(T)


def rho(S, K, T, sigma, option_type, r=0.04, q=0.0):
    _, d2 = _d1_d2(S, K, T, sigma, r, q)
    if option_type == 'call':
        return K * T * exp(-r * T) * norm.cdf(d2)
    return -K * T * exp(-r * T) * norm.cdf(-d2)


@dataclass
class Quote:
    """One snapshot of an option contract under BSM."""
    S: float
    K: float
    T: float
    sigma: float
    option_type: str
    r: float = 0.04
    q: float = 0.0

    @property
    def price(self):
        return price(self.S, self.K, self.T, self.sigma, self.option_type, self.r, self.q)

    @property
    def delta(self):
        return delta(self.S, self.K, self.T, self.sigma, self.option_type, self.r, self.q)

    @property
    def gamma(self):
        return gamma(self.S, self.K, self.T, self.sigma, self.r, self.q)

    @property
    def theta(self):
        return theta(self.S, self.K, self.T, self.sigma, self.option_type, self.r, self.q)

    @property
    def vega(self):
        return vega(self.S, self.K, self.T, self.sigma, self.r, self.q)


def strike_from_delta(S, T, sigma, target_delta, option_type, r=0.04, q=0.0):
    """
    Closed-form inverse: given a target |delta|, return the strike that achieves it.

    target_delta should be passed as a POSITIVE number (e.g. 0.22 for a 22-delta short put).
    The sign is inferred from option_type.
    """
    if not 0 < target_delta < 1:
        raise ValueError(f"target_delta must be in (0, 1); got {target_delta}")
    if T <= 0 or sigma <= 0:
        raise ValueError(f"T and sigma must be positive (T={T}, sigma={sigma})")

    # For a call:  delta = e^(-qT) * N(d1)        -> N(d1) = target * e^(qT)
    # For a put:   delta = -e^(-qT) * N(-d1)      -> N(-d1) = target * e^(qT)  -> d1 = -ppf(target*e^(qT))
    adj = target_delta * exp(q * T)
    if not 0 < adj < 1:
        raise ValueError(f"target_delta after dividend adjustment out of bounds: {adj}")

    if option_type == 'call':
        d1 = norm.ppf(adj)
    else:
        d1 = -norm.ppf(adj)

    vol_t = sigma * sqrt(T)
    # d1 = (ln(S/K) + (r - q + 0.5 sigma^2) T) / (sigma sqrt T)
    # -> ln(S/K) = d1 * vol_t - (r - q + 0.5 sigma^2) T
    # -> K = S * exp(-(d1 * vol_t - (r - q + 0.5 sigma^2) T))
    ln_S_over_K = d1 * vol_t - (r - q + 0.5 * sigma * sigma) * T
    return S / exp(ln_S_over_K)


def round_strike(K, increment=2.5):
    """Round to a tradeable strike increment (TSLA usually $2.50 or $5)."""
    return round(K / increment) * increment


def peek_position(S, dte, target_delta, side, iv, r=0.04, q=0.0, strike_increment=2.5):
    """v1.12 — return the would-be position's full greek set + derived metrics.

    Used by `adapt_entry_params` so adaptive rules can reason about option-side
    quantities (theta_yield, gamma_dollar, etc.) before the entry is finalized.

    Returns a dict; on pricing failure (invalid IV / DTE), returns dict with
    'valid': False so callers can skip cleanly.
    """
    out = {
        'valid': False,
        'strike': 0.0, 'credit': 0.0,
        'delta': 0.0, 'gamma': 0.0, 'theta': 0.0, 'vega': 0.0,
        'theta_per_day': 0.0, 'theta_yield': 0.0, 'gamma_dollar': 0.0,
    }
    if dte <= 0 or iv <= 0 or not (0 < target_delta < 1):
        return out
    T = dte / 365.0
    try:
        K_exact = strike_from_delta(S, T, iv, target_delta, side, r=r, q=q)
    except ValueError:
        return out
    K = round_strike(K_exact, strike_increment)
    if K <= 0:
        return out
    try:
        c = price(S, K, T, iv, side, r=r, q=q)
        d = delta(S, K, T, iv, side, r=r, q=q)
        g = gamma(S, K, T, iv, r=r, q=q)
        th = theta(S, K, T, iv, side, r=r, q=q)
        v = vega(S, K, T, iv, r=r, q=q)
    except (ValueError, ZeroDivisionError):
        return out
    if c <= 0:
        return out
    theta_per_day = th / 365.0
    out.update({
        'valid': True,
        'strike': float(K), 'credit': float(c),
        'delta': float(d), 'gamma': float(g),
        'theta': float(th), 'theta_per_day': float(theta_per_day),
        'vega': float(v),
        # Derived metrics that are scale-free and useful for cross-DTE comparisons
        'theta_yield': float(theta_per_day / c) if c > 0 else 0.0,  # per-day theta as fraction of credit
        'gamma_dollar': float(g * S * S * iv * iv / 365.0),         # expected daily P/L cost from gamma
    })
    return out


if __name__ == "__main__":
    S, sigma, dte = 445.0, 0.45, 30
    T = dte / 365.0

    print("=== Black-Scholes sanity check ===")
    print(f"S={S}  sigma={sigma}  DTE={dte}  T={T:.4f}")
    print()

    for option_type in ('put', 'call'):
        for tgt in (0.15, 0.20, 0.25, 0.30):
            K_exact = strike_from_delta(S, T, sigma, tgt, option_type)
            K = round_strike(K_exact, 2.5)
            q = Quote(S=S, K=K, T=T, sigma=sigma, option_type=option_type)
            print(f"{option_type:4s}  target_delta={tgt:.2f}  "
                  f"K_exact={K_exact:7.2f}  K={K:7.2f}  "
                  f"price={q.price:6.2f}  delta={q.delta:+.3f}  "
                  f"gamma={q.gamma:.4f}  theta/day={q.theta/365:+.3f}  "
                  f"vega/vol-pt={q.vega/100:.3f}")
        print()

    print("=== Sanity: inverse should round-trip ===")
    for option_type in ('put', 'call'):
        for tgt in (0.17, 0.22, 0.28):
            K = strike_from_delta(S, T, sigma, tgt, option_type)
            actual = abs(delta(S, K, T, sigma, option_type))
            print(f"{option_type:4s}  target={tgt:.3f}  recovered={actual:.3f}  "
                  f"diff={actual - tgt:+.2e}")
