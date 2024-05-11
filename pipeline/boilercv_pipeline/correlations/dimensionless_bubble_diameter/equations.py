"""Generated equations."""

from collections.abc import Hashable, Iterable, Mapping, Sequence
from pathlib import Path
from re import sub
from string import whitespace
from tomllib import loads
from typing import Generic, Literal, NamedTuple, TypeAlias, TypeVar

from numpy import float64, linspace
from numpy.typing import NDArray

from boilercv_pipeline.equations import MorphMap

Expectation: TypeAlias = float | Sequence[float] | NDArray[float64]
"""Expected result."""
Expectations: TypeAlias = dict[str, Expectation]
"""Expected results."""
Kind = Literal["latex", "sympy", "python"]
"""Kind."""
kinds: list[Kind] = ["latex", "sympy", "python"]
"""Equation kinds."""
Forms: TypeAlias = MorphMap[Kind, str]
"""Forms."""
FormsM: TypeAlias = Mapping[Kind, str]
"""Forms mapping."""
FormsD: TypeAlias = dict[Kind, str]
"""Forms dict."""

K = TypeVar("K", bound=Hashable)
V = TypeVar("V")
Kind_T = TypeVar("Kind_T", bound=Kind)
V_co = TypeVar("V_co", covariant=True)
Str_co = TypeVar("Str_co", covariant=True, bound=str)


EQUATIONS_TOML = Path(__file__).with_suffix(".toml")
"""TOML file with equations."""
EXPECTATIONS_TOML = Path(__file__).with_name("expectations.toml")
"""TOML file with equations."""


class Repl(NamedTuple, Generic[V_co, Str_co]):
    """Contents of `dst` to replace with `src`, with `find` substrings replaced with `repl`."""

    src: V_co
    """Source identifier."""
    dst: V_co
    """Destination identifier."""
    find: Str_co
    """Find this in the source."""
    repl: Str_co
    """Replacement for what was found."""


FormsRepl: TypeAlias = Repl[Kind, str]


MAKE_RAW = {'"': "'", r"\\": "\\"}
"""Replacement to turn escaped characters back to their raw form. Should be last."""
WHITESPACE_REPLS = tuple(
    FormsRepl(src=kind, dst=kind, find=find, repl=" ")
    for find in whitespace
    for kind in kinds
)
"""Whitespace replacements."""
LATEX_REPLS = tuple(
    FormsRepl(src="latex", dst="latex", find=find, repl=repl)
    for find, repl in {"{0}": r"\o", "{b0}": r"\b0"}.items()
)
"""Replacements to make after parsing LaTeX from PNGs."""


def set_forms_defaults(i: FormsM, name: str = "") -> FormsD:
    """Set default forms."""
    forms = dict(set_defaults(i, keys=kinds, default=""))
    if forms["sympy"] and not forms["latex"]:
        forms["latex"] = forms["sympy"]
    if not forms["latex"]:
        forms["latex"] = rf"\{name}"
    return forms


def handle_form_whitespace(i: FormsM) -> FormsD:
    """Handle whitespace in equation forms."""
    return replace(i, WHITESPACE_REPLS)


def set_defaults(
    i: Mapping[K, V_co], default: V_co, keys: Iterable[K] | None = None
) -> dict[K, V_co]:
    """Set defaults."""
    return {key: i.get(key, default) for key in [*i.keys(), *(keys or [])]}


def make_param(name: str, param: FormsD) -> Forms:
    """Make a parameter."""
    return (
        Forms(param)
        .pipe(set_defaults, keys=kinds, default="")
        .pipe(set_forms_defaults, name=name)
        .pipe(
            replace,
            repls=[
                FormsRepl(dst="sympy", src="latex", find=k, repl=v)
                for k, v in {r"_\b0": "_bo", r"_\o": "_0", "\\": ""}.items()
            ],
        )
    )


def replace(i: Mapping[K, str], repls: Sequence[Repl[K, str]]) -> dict[K, str]:
    """Make replacements from `Repl`s."""
    i = dict(i)
    for r in repls:
        i[r.dst] = i[r.src].replace(r.find, r.repl)
    return i


def regex_replace(i: Mapping[K, str], repls: Sequence[Repl[K, str]]) -> dict[K, str]:
    """Make regex replacements."""
    i = dict(i)
    for r in repls:
        i[r.dst] = sub(r.find, r.repl, i[r.src])
    return i


EXPECTATIONS = loads(EXPECTATIONS_TOML.read_text("utf-8"))
"""Expected results for the response of each correlation to `KWDS`."""
EQUATIONS = {
    name: Forms({"latex": eq["latex"], "sympy": eq["sympy"], "python": eq["python"]})
    .pipe(set_forms_defaults, name=name)
    .pipe(replace, repls=WHITESPACE_REPLS)
    for name, eq in loads(EQUATIONS_TOML.read_text("utf-8")).items()
}
"""Equations."""
LATEX_PARAMS = {
    name: make_param(name, param)
    for name, param in {
        "bubble_initial_reynolds": FormsD({"latex": r"\Re_\bo"}),
        "bubble_jakob": FormsD({"latex": r"\Ja"}),
        "bubble_fourier": FormsD({"latex": r"\Fo_\o"}),
        **{n: FormsD({"latex": f"\\{n}"}) for n in ["beta", "pi"]},
    }.items()
}
"""Parameters for function calls."""
SUBS = {arg["sympy"]: name for name, arg in LATEX_PARAMS.items()}
"""Substitutions from SymPy symbolic variables to descriptive names."""
KWDS: Expectations = {
    "dimensionless_bubble_diameter": 1.0,
    "bubble_initial_reynolds": 100.0,
    "bubble_jakob": 1.0,
    "bubble_fourier": linspace(start=0.0, stop=5.0e-3, num=10),
    "liquid_prandtl": 1.0,
}
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
