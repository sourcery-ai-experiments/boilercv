"""Parse equations."""

# /// script
# requires-python = "==3.11"
# dependencies = ["antlr4-python3-runtime==4.11", "sympy>=1.12"]
# ///

# THE FOLLOWING `docs/pyproject.toml` configuration DOESN'T WORK:
# # ? For `sympy.parsing.latex.parse_latex`
# # ? https://github.com/facebookresearch/hydra/issues/2699
# "antlr4-python3-runtime==4.11",
# # ? https://github.com/facebookresearch/hydra/pull/2733
# # ? https://github.com/facebookresearch/hydra/pull/2881
# "hydra-core @ git+https://github.com/facebookresearch/hydra@2e682d84e789d82dd11ab1f329f2dd1966fa6b54",
# # ? https://github.com/omry/omegaconf/pull/1114
# "omegaconf==2.4.0.dev2",
# antlr4-python3-runtime==4.11
#
# So we use `pipx` to isolate this script's dependencies from the rest of the project.

from json import dumps
from pathlib import Path

from sympy.parsing.latex import parse_latex
from sympy.utilities.lambdify import lambdastr

# from sympy import pi

N = 100
SUBS = {
    "Fo_{0}": "bubble_fourier",
    "Ja": "bubble_jakob",
    # "pi": pi,
}
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


def main():  # noqa: D103
    Path("lambdas.json").write_text(encoding="utf-8", data=dumps(LAMBDAS, indent=2))


if __name__ == "__main__":
    main()
