"""Generated equations."""

from collections.abc import Hashable, MutableMapping, Sequence
from pathlib import Path
from re import sub
from string import whitespace
from tomllib import loads
from typing import Annotated, Generic, Literal, NamedTuple, TypeAlias, TypeVar

from numpy import float64, linspace
from numpy.typing import NDArray
from pydantic import PlainSerializer, PlainValidator, model_validator
from pydantic_core import PydanticUndefinedType
from sympy import Expr, symbols

from boilercv_pipeline.equations import Morph

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
(
    bubble_fourier,
    bubble_jakob,
    bubble_initial_reynolds,
    liquid_prandtl,
    dimensionless_bubble_diameter,
) = SYMS
LONG_SYMS = symbols(list(SUBS.values()))
"""Symbols with long names."""
LOCALS = dict(zip(SUBS.keys(), SYMS, strict=False))
"""Local variables for sympyfying."""


Expectation: TypeAlias = float | Sequence[float] | NDArray[float64]
"""Expected result."""
Expectations: TypeAlias = dict[str, Expectation]
"""Expected results."""

Kind = Literal["latex", "sympy", "python"]
"""Kind."""
kinds: list[Kind] = ["latex", "sympy", "python"]
"""Equation kinds."""
FormsM: TypeAlias = Morph[Kind, str]
"""Forms."""


class Forms(FormsM):
    """Forms."""

    @model_validator(mode="before")
    @classmethod
    def set_defaults(cls, data):
        """Set missing kinds to an empty string."""
        return dict.fromkeys(kinds, "") | (
            {} if isinstance(data, PydanticUndefinedType) else data
        )


params = ["Fo_0", "Ja", "Re_b0", "Pr", "beta"]
"""Parameters."""
Param = Literal["Fo_0", "Ja", "Re_b0", "Pr", "beta"]
"""Parameter."""
Exprs = list[Expr]
"""Expressions."""


def validate_solutions(v: Exprs) -> Exprs:
    """Validate solutions."""
    for expr in v:
        for sym in expr.free_symbols:
            if sym not in LOCALS.values():
                raise ValueError(f"Got unexpected symbol '{sym}'.")
    return v


def serialize_solutions(x: Exprs) -> list[str]:
    """Serialize solutions."""
    return [str(expr) for expr in x]


SolnsM = Morph[
    Param,
    Annotated[Exprs, PlainSerializer(lambda v: v), PlainValidator(validate_solutions)],
]


class Solns(SolnsM):
    """Solution forms."""

    @model_validator(mode="before")
    @classmethod
    def set_defaults(cls, data):
        """Set missing solutions to empty lists."""
        return {k: [] for k in params} | (
            {} if isinstance(data, PydanticUndefinedType) else data
        )


d = Solns({"Fo_0": [LOCALS["Fo_0"]]})
# d.model_dump_json()

T = TypeVar("T")
K = TypeVar("K", bound=Hashable)
V = TypeVar("V")


EQUATIONS_TOML = Path(__file__).with_suffix(".toml")
"""TOML file with equations."""
EXPECTATIONS_TOML = Path(__file__).with_name("expectations.toml")
"""TOML file with equations."""


class Repl(NamedTuple, Generic[T]):
    """Contents of `dst` to replace with `src`, with `find` substrings replaced with `repl`."""

    src: T
    """Source identifier."""
    dst: T
    """Destination identifier."""
    find: str
    """Find this in the source."""
    repl: str
    """Replacement for what was found."""


FormsRepl: TypeAlias = Repl[Kind]


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


def replace(
    i: MutableMapping[K, str], repls: Sequence[Repl[K]]
) -> MutableMapping[K, str]:
    """Make replacements from `Repl`s."""
    for r in repls:
        i[r.dst] = i[r.src].replace(r.find, r.repl)
    return i


def regex_replace(
    i: MutableMapping[K, str], repls: Sequence[Repl[K]]
) -> MutableMapping[K, str]:
    """Make regex replacements."""
    for r in repls:
        i[r.dst] = sub(r.find, r.repl, i[r.src])
    return i


def handle_form_whitespace(i: MutableMapping[K, str]) -> MutableMapping[K, str]:
    """Handle whitespace in equation forms."""
    return replace(i, WHITESPACE_REPLS)


def set_equation_forms(i: FormsM) -> FormsM:
    """Set equation forms."""
    i = i.pipe(handle_form_whitespace).pipe(
        replace,
        tuple(
            FormsRepl(src="sympy", dst="sympy", find=find, repl=repl)
            for find, repl in {"{o}": "0", "{bo}": "b0"}.items()
        ),
    )
    if not i.get("sympy"):
        return i.model_dump()
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
    ).model_dump()


EXPECTATIONS = loads(EXPECTATIONS_TOML.read_text("utf-8"))
"""Expected results for the response of each correlation to `KWDS`."""
EQUATIONS = {
    name: Forms(eq).pipe(set_equation_forms)
    for name, eq in loads(EQUATIONS_TOML.read_text("utf-8")).items()
}
"""Equations."""


def set_param_forms(i: FormsM, name: str = "") -> FormsM:
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

FOO = {name: Forms(param) for name, param in LATEX_PARAMS.items()}

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
