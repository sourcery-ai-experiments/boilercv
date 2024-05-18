"""Morphs."""

from collections.abc import Iterable
from contextlib import nullcontext
from pathlib import Path
from re import sub
from string import whitespace
from typing import Annotated, Any, ClassVar, Generic, Self, TypeAlias

from numpy import linspace, pi
from pydantic import BaseModel, Field, PlainSerializer, PlainValidator, model_validator
from pydantic_core import PydanticUndefinedType
from sympy import Basic, symbols, sympify
from tomlkit import TOMLDocument, parse
from tomlkit.items import Table

from boilercv_pipeline.correlations.dimensionless_bubble_diameter.types import (
    Eq,
    Expectation,
    FormsRepl,
    JsonStrPlainSerializer,
    K,
    Kind,
    Param,
    Repl,
    Sym,
    V,
    kinds,
    params,
    syms,
)
from boilercv_pipeline.equations import BaseMorph, Morph

base = Path(__file__).with_suffix(".toml")
EQUATIONS_TOML = base.with_stem("equations")
"""TOML file with equations."""
EXPECTATIONS_TOML = base.with_stem("expectations")
"""TOML file with expectations."""
SOLUTIONS_TOML = base.with_stem("solutions")
"""TOML file with solutions."""
EXPECTATIONS = parse(EXPECTATIONS_TOML.read_text("utf-8"))
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
KWDS = Morph[Param, Expectation]({
    "bubble_fourier": linspace(start=0.0, stop=5.0e-3, num=10),
    "bubble_jakob": 1.0,
    "bubble_initial_reynolds": 100.0,
    "liquid_prandtl": 1.0,
    "dimensionless_bubble_diameter": 1.0,
    "pi": pi,
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


DefaultMorph.register(Forms)


def validate_expr(v: Basic | str):
    """Validate expression."""
    return (
        v
        if isinstance(v, Basic)
        else sympify(v, locals=LOCALS.model_dump(), evaluate=False)
    )


Expr: TypeAlias = Annotated[
    Basic, PlainValidator(validate_expr), JsonStrPlainSerializer
]
"""Expression."""
solve_syms: tuple[Sym, ...] = ("Fo_0", "beta")
"""Symbols to solve for."""


class Soln(BaseModel):
    """All solutions."""

    solutions: list[Expr] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


class Solns(DefaultMorph[Sym, Soln]):
    """Solution forms."""

    default_keys: ClassVar[tuple[Sym, ...]] = solve_syms
    default_factory: ClassVar = Soln


DefaultMorph.register(Solns)


Locals: TypeAlias = Morph[Sym, Expr]
"""Locals."""
LOCALS = Locals(
    dict(
        zip(
            syms,
            symbols(list(PARAMS.values()), nonnegative=True, real=True, finite=True),
            strict=False,
        )
    )
)
"""Local variables."""


def set_equation_forms(i: Forms, symbols: Locals) -> Forms:
    """Set equation forms."""
    return i.pipe(
        replace,
        (
            FormsRepl(src="sympy", dst="sympy", find=find, repl=repl)
            for find, repl in {"{o}": "0", "{bo}": "b0"}.items()
        ),
    ).pipe(
        regex_replace,
        (
            FormsRepl(src="sympy", dst="sympy", find=find, repl=repl)
            for sym in symbols
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


EQUATIONS = Morph[Eq, Forms]({
    name: Forms(eq)  # pyright: ignore[reportArgumentType]
    .pipe(
        replace,
        (
            FormsRepl(src=kind, dst=kind, find=find, repl=" ")
            for find in whitespace
            for kind in kinds
        ),
    )
    .pipe(set_equation_forms, symbols=LOCALS)
    for name, eq in parse(EQUATIONS_TOML.read_text("utf-8")).items()
})
"""Equations."""


class TomlMorph(BaseMorph[K, V], Generic[K, V]):
    """Morphable mapping."""

    root: Morph[K, V] = Field(default_factory=Morph[K, V])
    toml: Annotated[
        TOMLDocument,
        PlainValidator(lambda v: v),
        PlainSerializer(lambda v: dict(v), return_type=dict, when_used="json"),
    ] = Field(default_factory=TOMLDocument)

    def sync(
        self, root: Self | None = None, toml: TOMLDocument | None = None
    ) -> Self | None:
        """Sync TOML with root."""
        # TODO: This force-updates every key in TOML. Only update if keys are different after pre-processing.
        # TODO: Fix type-hints with a recursive type hint.
        if not toml:
            toml = self.toml
        with nullcontext() if root else self.thaw() as synced_copy:
            src: dict[Any, Any] = root or synced_copy.root.model_dump(mode="json")  # pyright: ignore[reportAssignmentType, reportOptionalMemberAccess]
            for key in src:
                if (
                    key in toml
                    and isinstance(src[key], dict)
                    and isinstance(toml[key], Table)
                ):  # pyright: ignore[reportArgumentType]
                    self.sync(src[key], toml[key])  # pyright: ignore[reportArgumentType]
                    continue
                toml[key] = src[key]
            for key in [k for k in toml if k not in src]:
                del toml[key]
        return synced_copy

    @classmethod
    def make(cls, toml: Path) -> Self:  # noqa: D102
        data = parse(toml.read_text("utf-8"))
        return cls(toml=data, root=data)  # pyright: ignore[reportArgumentType]


class Solns2(TomlMorph[Eq, Solns]):
    """Morph with underlying TOML type and defaults."""


SOLUTIONS = Solns2.make(toml=SOLUTIONS_TOML)
"""Solutions."""

SOLUTIONS.sync()
