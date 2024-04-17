"""Parse equations."""

from sympy import pi
from sympy.parsing.latex import parse_latex
from sympy.utilities.lambdify import lambdastr

# antlr4-python3-runtime==4.11

N = 100
SUBS = {"Fo_{0}": "bubble_fourier", "Ja": "bubble_jakob", "pi": pi}
KWDS = dict(n=N, subs=SUBS, strict=True)
CORRELATIONS = {
    "dimensionless_bubble_diameter_florschuetz_chao_1965": r"\beta = 1 - 4\Ja\sqrt{\Fo_0/\pi}"
}
LAMBDAS = {
    source: lambdastr(
        expr=parse_latex(correlation).rhs.evalf(n=N, subs=SUBS, strict=True),
        args=["bubble_fourier", "bubble_jakob"],
    )
    for source, correlation in CORRELATIONS.items()
}
