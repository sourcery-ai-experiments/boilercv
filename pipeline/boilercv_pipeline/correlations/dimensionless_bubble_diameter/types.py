"""Types."""

from collections.abc import Hashable
from typing import Annotated, Generic, Literal, NamedTuple, TypeAlias, TypeVar, get_args

from numpy import float64
from numpy.typing import NDArray
from pydantic import PlainSerializer, PlainValidator
from sympy import Basic

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


Sym: TypeAlias = Literal["Fo_0", "Ja", "Re_b0", "Pr", "beta", "pi"]
"""Symbol."""
Kind: TypeAlias = Literal["latex", "sympy", "python"]
"""Kind."""
FormsRepl: TypeAlias = Repl[Kind]
"""Forms replacements."""
Param: TypeAlias = Literal[
    "bubble_fourier",
    "bubble_jakob",
    "bubble_initial_reynolds",
    "liquid_prandtl",
    "dimensionless_bubble_diameter",
    "pi",
]
"""Parameter."""
JsonStrPlainSerializer = PlainSerializer(
    lambda v: str(v), return_type=str, when_used="json"
)
"""Serializer that stringifies values only when serializing to JSON."""
Expectation: TypeAlias = (
    float
    | Annotated[NDArray[float64], PlainValidator(lambda v: v), JsonStrPlainSerializer]
)
"""Expected result."""
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
    Basic, PlainValidator(validate_expr), JsonStrPlainSerializer
]
"""Expression."""
