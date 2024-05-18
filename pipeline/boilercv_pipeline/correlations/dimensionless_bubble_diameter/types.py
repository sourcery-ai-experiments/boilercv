"""Types."""

from typing import Annotated, Generic, Literal, NamedTuple, TypeAlias, TypeVar, get_args

from numpy import float64
from numpy.typing import NDArray
from pydantic import PlainSerializer, PlainValidator

T = TypeVar("T")
K = TypeVar("K")
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


Eq: TypeAlias = Literal[
    "florschuetz_chao_1965", "isenberg_sideman_1970", "akiyama_1973", "yuan_et_al_2009"
]
"""Equation."""
Kind: TypeAlias = Literal["latex", "sympy", "python"]
"""Kind."""
kinds: tuple[Kind, ...] = get_args(Kind)
"""Equation kinds."""
Sym: TypeAlias = Literal["Fo_0", "Ja", "Re_b0", "Pr", "beta", "pi"]
"""Symbol."""
syms: tuple[Sym, ...] = get_args(Sym)
"""Symbols."""
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
params: tuple[Param, ...] = get_args(Param)
"""Parameters."""
JsonStrPlainSerializer = PlainSerializer(
    lambda v: str(v), return_type=str, when_used="json"
)
"""Serializer that stringifies values only when serializing to JSON."""
Expectation: TypeAlias = (
    float
    | Annotated[NDArray[float64], PlainValidator(lambda v: v), JsonStrPlainSerializer]
)
"""Expected result."""
