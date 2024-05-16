"""Generated equations."""

import math
from pathlib import Path
from tomllib import loads

from numpy import linspace
from sympy import symbols

from boilercv_pipeline.correlations.dimensionless_bubble_diameter.morphs import (
    Forms,
    regex_replace,
    replace,
)
from boilercv_pipeline.correlations.dimensionless_bubble_diameter.types import (
    Expectation,
    Expr,
    FormsRepl,
    Param,
    Sym,
    params,
    syms,
)
from boilercv_pipeline.equations import Morph

EQUATIONS_TOML = Path(__file__).with_suffix(".toml")
"""TOML file with equations."""
EXPECTATIONS_TOML = Path(__file__).with_name("expectations.toml")
"""TOML file with equations."""
EXPECTATIONS = loads(EXPECTATIONS_TOML.read_text("utf-8"))
"""Expected results for the response of each correlation to `KWDS`."""
MAKE_RAW = {'"': "'", r"\\": "\\"}
"""Replacement to turn escaped characters back to their raw form. Should be last."""
LATEX_REPLS = tuple(
    FormsRepl(src="latex", dst="latex", find=find, repl=repl)
    for find, repl in {"{0}": r"\o", "{b0}": r"\b0"}.items()
)
"""Replacements to make after parsing LaTeX from PNGs."""
PARAMS = Morph[Param, Sym](dict(zip(params, syms, strict=True)))
"""Parameters."""
SYMBOLS = symbols(list(PARAMS.values()))
"""Symbols."""
LOCALS = Morph[Sym, Expr](dict(zip(syms, SYMBOLS, strict=False)))
"""Local variables for sympyfying."""
KWDS = Morph[Param, Expectation]({
    "bubble_fourier": linspace(start=0.0, stop=5.0e-3, num=10),
    "bubble_jakob": 1.0,
    "bubble_initial_reynolds": 100.0,
    "liquid_prandtl": 1.0,
    "dimensionless_bubble_diameter": 1.0,
    "pi": math.pi,
})
"""Common keyword arguments applied to correlations.

A single test condition has been chosen to exercise each correlation across as wide of a
range as possible without returning `np.nan` values. This is done as follows:

- Let `bubble_initial_reynolds`,
`liquid_prandtl`, and `bubble_jakob` be 100.0, 1.0, and 1.0, respectively.
- Apply the correlation `dimensionless_bubble_diameter_tang_et_al_2016` with
`bubble_fourier` such that the `dimensionless_bubble_diameter` is very close to zero.
This is the correlation with the most rapidly vanishing value of
`dimensionless_bubble_diameter`.
- Choose ten linearly-spaced points for `bubble_fourier` between `0` and the maximum
`bubble_fourier` just found.
"""


def set_equation_forms(i: Forms) -> Forms:
    """Set equation forms."""
    i = i.pipe(
        replace,
        tuple(
            FormsRepl(src="sympy", dst="sympy", find=find, repl=repl)
            for find, repl in {"{o}": "0", "{bo}": "b0"}.items()
        ),
    )
    if not i["sympy"]:
        return i
    return i.pipe(
        regex_replace,
        tuple(
            FormsRepl(src="sympy", dst="sympy", find=find, repl=repl)
            for sym in LOCALS
            for find, repl in {
                # ? Symbol split by `(` after first character.
                rf"{sym[0]}\*\({sym[1:]}([^)]+)\)": rf"{sym}\g<1>",
                # ? Symbol split by a `*` after first character.
                rf"{sym[0]}\*{sym[1:]}": rf"{sym}",
                # ? Symbol missing `*` resulting in failed attempt to call it
                rf"{sym}\(": rf"{sym}*(",
            }.items()
        ),
    )


EQUATIONS = {
    name: Forms(eq).pipe(set_equation_forms)
    for name, eq in loads(EQUATIONS_TOML.read_text("utf-8")).items()
}
"""Equations."""


def set_param_forms(i: Forms, name: str = "") -> Forms:
    """Set forms for parameters."""
    if i["sympy"] and not i["latex"]:
        i["latex"] = i["sympy"]
    if not i["latex"]:
        i["latex"] = rf"\{name}"
    return i


LATEX_PARAMS = {
    name: (
        param.pipe(set_param_forms, name=name).pipe(
            replace,
            repls=[
                FormsRepl(src="latex", dst="sympy", find=k, repl=v)
                for k, v in {r"_\b0": "_bo", r"_\o": "_0", "\\": ""}.items()
            ],
        )
    )
    for name, param in {
        "bubble_initial_reynolds": Forms({"latex": r"\Re_\bo"}),
        "bubble_jakob": Forms({"latex": r"\Ja"}),
        "bubble_fourier": Forms({"latex": r"\Fo_\o"}),
        **{n: Forms({"latex": f"\\{n}"}) for n in ["beta", "pi"]},
    }.items()
}
"""Parameters for function calls."""
SYMPY_SUBS = {arg["sympy"]: name for name, arg in LATEX_PARAMS.items()}
"""Substitutions from SymPy symbolic variables to descriptive names."""
