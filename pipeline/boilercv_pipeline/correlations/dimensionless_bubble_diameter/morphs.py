"""Morphs."""

from collections.abc import Iterable
from re import sub
from string import whitespace
from typing import Any, ClassVar, Generic, Self

from pydantic import model_validator
from pydantic_core import PydanticUndefinedType
from typing_extensions import TypedDict

from boilercv_pipeline.correlations.dimensionless_bubble_diameter.types import (
    Expr,
    FormsRepl,
    K,
    Kind,
    Repl,
    Sym,
    V,
    kinds,
)
from boilercv_pipeline.equations import Morph


def replace(i: dict[K, str], repls: Iterable[Repl[K]]) -> dict[K, str]:
    """Make replacements from `Repl`s."""
    for r in repls:
        i[r.dst] = i[r.src].replace(r.find, r.repl)
    return i


def regex_replace(i: dict[K, str], repls: Iterable[Repl[K]]) -> dict[K, str]:
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


class Forms(DefaultMorph[Kind, str]):
    """Forms."""

    default_keys: ClassVar = kinds
    default: ClassVar = ""

    @model_validator(mode="after")
    def handle_whitespace(self):
        """Handle whitespace in equation forms."""
        return self.model_construct(
            replace(
                dict(self),
                (
                    FormsRepl(src=kind, dst=kind, find=find, repl=" ")
                    for find in whitespace
                    for kind in kinds
                ),
            )
        )


DefaultMorph.register(Forms)

solve_syms: tuple[Sym, ...] = ("Fo_0", "beta")


class Soln(TypedDict):
    """All solutions."""

    solutions: list[Expr]
    warnings: list[str]


class Solns(DefaultMorph[Sym, Soln]):
    """Solution forms."""

    default_keys: ClassVar[tuple[Sym, ...]] = solve_syms
    default_factory: ClassVar = list


DefaultMorph.register(Solns)
