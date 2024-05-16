"""Generated equations."""

from collections.abc import Hashable, Sequence
from pathlib import Path
from re import sub
from string import whitespace
from tomllib import loads
from typing import (
    Annotated,
    Any,
    ClassVar,
    Generic,
    Literal,
    NamedTuple,
    Self,
    TypeAlias,
    TypeVar,
    get_args,
)

from numpy import float64, linspace
from numpy.typing import NDArray
from pydantic import PlainSerializer, PlainValidator, model_validator
from pydantic_core import PydanticUndefinedType
from sympy import Basic, symbols

from boilercv_pipeline.equations import Morph

T = TypeVar("T", bound=Hashable)
K = TypeVar("K", bound=Hashable)
V = TypeVar("V")


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


def replace(i: dict[K, str], repls: Sequence[Repl[K]]) -> dict[K, str]:
    """Make replacements from `Repl`s."""
    for r in repls:
        i[r.dst] = i[r.src].replace(r.find, r.repl)
    return i


def regex_replace(i: dict[K, str], repls: Sequence[Repl[K]]) -> dict[K, str]:
    """Make regex replacements."""
    for r in repls:
        i[r.dst] = sub(r.find, r.repl, i[r.src])
    return i


class DefaultMorph(Morph[K, V], Generic[K, V]):
    """Morph with default values."""

    default_keys: ClassVar[tuple[Any, ...]] = ()
    """Default keys."""
    default: ClassVar = None
    """Default value."""
    default_factory: ClassVar = None
    """Default value factory."""

    @model_validator(mode="before")
    @classmethod
    def set_defaults(cls, data: dict[K, V]) -> Self | dict[K, V]:
        """Set `self.default_keys` using `self.default_factory` or `self.default`."""
        if not cls.default_keys:
            return data
        if isinstance(data, PydanticUndefinedType) or any(
            key not in data for key in cls.default_keys
        ):
            return dict.fromkeys(  # pyright: ignore[reportReturnType]  # Eventually valid
                cls.default_keys,
                cls.default_factory() if cls.default_factory else cls.default,
            ) | ({} if isinstance(data, PydanticUndefinedType) else data)
        return data


Sym: TypeAlias = Literal["Fo_0", "Ja", "Re_b0", "Pr", "beta", "pi"]
"""Symbol."""
Kind: TypeAlias = Literal["latex", "sympy", "python"]
"""Kind."""
FormsRepl: TypeAlias = Repl[Kind]
Param: TypeAlias = Literal[
    "bubble_fourier",
    "bubble_jakob",
    "bubble_initial_reynolds",
    "liquid_prandtl",
    "beta",
    "pi",
]
"""Parameter."""
Expectation: TypeAlias = float | Sequence[float] | NDArray[float64]
"""Expected result."""
Expectations: TypeAlias = dict[str, Expectation]
"""Expected results."""

syms: tuple[Sym, ...] = get_args(Sym)
"""Symbols."""
kinds: tuple[Kind, ...] = get_args(Kind)
"""Equation kinds."""
params: tuple[Param, ...] = get_args(Param)
"""Parameters."""


def validate_expr(v: Basic):
    """Validate expression."""
    if unexpected_syms := [str(sym) for sym in v.free_symbols if str(sym) not in syms]:
        raise ValueError(f"Got unexpected symbols: {', '.join(unexpected_syms)}")
    return v


Expr: TypeAlias = Annotated[
    Basic, PlainValidator(validate_expr), PlainSerializer(lambda v: str(v))
]
"""Expression."""

EQUATIONS_TOML = Path(__file__).with_suffix(".toml")
"""TOML file with equations."""
EXPECTATIONS_TOML = Path(__file__).with_name("expectations.toml")
"""TOML file with equations."""
PARAMS = Morph[Param, Sym](dict(zip(params, syms, strict=True)))
"""Parameters."""
SUBS = Morph[Sym, str]({
    "Fo_0": "bubble_fourier",
    "Ja": "bubble_jakob",
    "Re_b0": "bubble_initial_reynolds",
    "Pr": "liquid_prandtl",
    "beta": "dimensionless_bubble_diameter",
})
"""Substitutions."""
SYMS = symbols(list(PARAMS.values()))
"""Symbols."""
(Fo_0, Ja, Re_b0, Pr, beta, pi) = SYMS
LOCALS = Morph[Sym, Expr](dict(zip(SUBS.keys(), SYMS, strict=False)))
"""Local variables for sympyfying."""
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


class Forms(DefaultMorph[Kind, str]):
    """Forms."""

    default_keys: ClassVar = kinds
    default: ClassVar = ""

    @model_validator(mode="after")
    def handle_whitespace(self):
        """Handle whitespace in equation forms."""
        return self.model_construct(replace(dict(self), WHITESPACE_REPLS))


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


EXPECTATIONS = loads(EXPECTATIONS_TOML.read_text("utf-8"))
"""Expected results for the response of each correlation to `KWDS`."""
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

FOO = {name: Forms(param) for name, param in LATEX_PARAMS.items()}


class Solns(DefaultMorph[Sym, list[Expr]]):
    """Solution forms."""

    default_keys: ClassVar = syms
    default_factory: ClassVar = list
