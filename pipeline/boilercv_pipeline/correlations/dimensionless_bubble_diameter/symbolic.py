"""Symbolic dimensionless bubble diameter correlations for bubble collapse."""

from sympy import Eq, pi, sqrt, symbols

N = 100
"""Numerical evaluation precision."""
SUBS = {
    "Fo_0": "bubble_fourier",
    "Ja": "bubble_jakob",
    "Re_b0": "bubble_initial_reynolds",
    "Pr": "liquid_prandtl",
    "beta": "dimensionless_bubble_diameter",
}
"""Substitutions."""
SYMS = symbols(list(SUBS))
"""Symbols."""
(Fo_0, Ja, Re_b0, Pr, beta) = SYMS
LONG_SYMS = symbols(list(SUBS.values()))
"""Symbols with long names."""
LOCALS = dict(zip(SUBS.keys(), SYMS, strict=False))
"""Local variables for sympyfying."""
(
    bubble_fourier,
    bubble_jakob,
    bubble_initial_reynolds,
    liquid_prandtl,
    dimensionless_bubble_diameter,
) = SYMS

florschuetz_chao_1965 = Eq(beta, 1 - 4 * Ja * sqrt(Fo_0 / pi))
