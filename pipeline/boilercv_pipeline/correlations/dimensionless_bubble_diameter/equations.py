"""Generated equations."""

from collections.abc import Hashable, Iterable, Mapping, Sequence
from pathlib import Path
from tomllib import loads
from typing import Literal, TypeAlias, TypeVar

from numpy import float64, linspace
from numpy.typing import NDArray

from boilercv_pipeline.equations import MorphMap

Expectation: TypeAlias = float | Sequence[float] | NDArray[float64]
"""Expected result."""
Expectations: TypeAlias = dict[str, Expectation]
"""Expected results."""
Kind: TypeAlias = Literal["latex", "sympy", "python"]
"""Equation kind."""
Form: TypeAlias = str
"""Equation form."""
kinds: list[Kind] = ["latex", "sympy", "python"]
"""Equation kinds."""

Forms = MorphMap[Kind, Form]
"""Forms `MorphMap`."""
M = Mapping[Kind, Form]
"""Forms dictionary."""
D = dict[Kind, Form]
"""Forms dictionary."""

EQUATIONS_TOML = Path(__file__).with_suffix(".toml")
"""TOML file with equations."""
EXPECTATIONS_TOML = Path(__file__).with_name("expectations.toml")
"""TOML file with equations."""


def make_param(name: str, param: M) -> Forms:
    """Make a parameter."""
    return (
        Forms.make(param)
        .pipe(set_forms_defaults, name=name)
        .pipe(
            f=replace,
            repls={
                ("latex", k): ("sympy", v)
                for k, v in {r"_\b0": "_bo", r"_\o": "_0", "\\": ""}.items()
            },
        )
    )


def set_forms_defaults(m: M, name: str = "") -> M:
    """Set default forms."""
    forms = Forms.make(m).pipe(set_defaults, keys=kinds, default="").asdict()
    if forms["sympy"] and not forms["latex"]:
        forms["latex"] = forms["sympy"]
    if not forms["latex"]:
        forms["latex"] = rf"\{name}"
    return forms


K = TypeVar("K", bound=Hashable)
V = TypeVar("V", covariant=True)


def set_defaults(
    m: Mapping[K, V], default: V, keys: Iterable[K] | None = None
) -> Mapping[K, V]:
    """Set defaults."""
    return {key: m.get(key, default) for key in [*m.keys(), *(keys or [])]}


def replace(m: M, repls: dict[tuple[Kind, str], tuple[Kind, str]]) -> M:
    """Replace matching forms in `src`."""
    m = dict(m)
    for (old_kind, old), (new_kind, new) in repls.items():
        m[new_kind] = m[old_kind].replace(old, new)
    return m


args = {
    name: make_param(name, param)
    for name, param in {
        "bubble_initial_reynolds": D({"latex": r"\Re_\bo"}),
        "bubble_jakob": D({"latex": r"\Ja"}),
        "bubble_fourier": D({"latex": r"\Fo_\o"}),
    }.items()
}


params = {
    name: make_param(name, param)
    for name, param in {n: D({"latex": f"\\{n}"}) for n in ["beta", "pi"]}.items()
}


EQUATIONS = {
    eq["name"]: Forms.make({
        "latex": eq["latex"],
        "sympy": eq["sympy"],
        "python": eq["python"],
    })
    .pipe(set_forms_defaults, name=eq["name"])
    .pipe(
        replace,
        repls={
            (src, k): (src, v)
            for (k, v) in {"\n": "", "    ": ""}.items()
            for src in kinds
        },
    )
    for eq in loads(EQUATIONS_TOML.read_text("utf-8"))["equation"]
}


MAKE_RAW = {r"\\": "\\"}
"""Replacement to turn escaped characters in strings back to their raw form."""
SYMPY_REPL = {"{o}": "0", "{bo}": "b0"} | MAKE_RAW
"""Replacements after parsing LaTeX to SymPy."""
LATEX_REPL = {"{0}": r"\o", "{b0}": r"\b0"} | MAKE_RAW
"""Replacements to make after parsing LaTeX from PNGs."""


SUBS = {arg["sympy"]: name for name, arg in (args | params).items()}
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

EXPECTATIONS = loads(EXPECTATIONS_TOML.read_text("utf-8"))
"""Expected results for the response of each correlation to `KWDS`."""
