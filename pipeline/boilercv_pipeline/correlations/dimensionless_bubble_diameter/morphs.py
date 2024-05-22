"""Morphs."""

from collections.abc import Iterable, MutableMapping
from pathlib import Path
from re import sub
from string import whitespace
from typing import Any, ClassVar, Generic, Self, overload

from numpy import linspace, pi
from pydantic import BaseModel, Field, model_validator
from pydantic_core import PydanticUndefinedType
from tomlkit import parse
from tomlkit.container import Container
from tomlkit.items import Item

from boilercv.morphs import BaseMorph, Morph
from boilercv_pipeline.correlations.dimensionless_bubble_diameter.types import (
    LOCALS,
    Eq,
    Expectation,
    Expr,
    FormsRepl,
    K,
    Kind,
    Leaf,
    Locals,
    Node,
    Param,
    Repl,
    Sym,
    V,
    kinds,
    solve_syms,
)

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


class Soln(BaseModel):
    """All solutions."""

    solutions: list[Expr] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


class Solns(DefaultMorph[Sym, Soln]):
    """Solution forms."""

    default_keys: ClassVar[tuple[Sym, ...]] = solve_syms
    default_factory: ClassVar = Soln


DefaultMorph.register(Solns)


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

    path: Path
    root: Morph[K, V] = Field(default_factory=Morph[K, V])

    # ! Root case
    @overload
    def sync(self, src: None = None, dst: None = None) -> Container: ...
    # ! General case
    @overload
    def sync(self, src: Node | Leaf, dst: Item | Container) -> None: ...
    # ! Union
    def sync(
        self, src: Node | Leaf | None = None, dst: Item | Container | None = None
    ) -> Container | None:
        """Sync a TOML document."""
        if not src:
            model_dump: Node = self.root.model_dump(mode="json")
            src = model_dump
        dst = dst or parse(self.path.read_text("utf-8"))
        if not isinstance(dst, MutableMapping):
            return
        for key in [k for k in dst if k not in src]:
            del dst[key]
        for key in src:
            if key in dst:
                if src[key] == dst[key]:
                    continue
                if isinstance(src[key], dict) and isinstance(dst[key], MutableMapping):
                    self.sync(src[key], dst[key])
                    continue
            dst[key] = src[key]
        return dst

    def write(self) -> None:
        """Write to TOML."""
        self.path.write_text(self.sync().as_string(), "utf-8")

    @classmethod
    def read(cls, path: Path) -> Self:
        """Read from TOML."""
        return cls(path=path, root=parse(path.read_text("utf-8")))  # type: ignore[reportArgumentType]


class TomlSolns(TomlMorph[Eq, Solns]):
    """Morph with underlying TOML type and defaults."""


SOLUTIONS = TomlSolns.read(path=SOLUTIONS_TOML)
"""Solutions."""
