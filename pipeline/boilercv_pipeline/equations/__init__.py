"""Equations."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Mapping, Sequence
from pathlib import Path
from shlex import quote
from typing import Any, Generic, Literal, TypeAlias, TypeVar

from numpy import float64
from numpy.typing import NDArray
from pydantic import BaseModel, Field, RootModel

PIPX = quote((Path(".venv") / "scripts" / "pipx").as_posix())
"""Escaped path to `pipx` executable suitable for `subprocess.run` invocation."""


KT = TypeVar("KT")
VT = TypeVar("VT")


class MappingModel(RootModel[Mapping[KT, VT]], Mapping[KT, VT], Generic[KT, VT]):
    root: Mapping[KT, VT] = Field(default_factory=dict)

    def __len__(self):
        return len(self.root)

    def __getitem__(self, key):
        if key in self.root:
            return self.root[key]
        if hasattr(self.__class__, "__missing__"):
            return self.__class__.__missing__(self, key)
        raise KeyError(key)

    def __setitem__(self, key, item):
        self.root[key] = item

    def __delitem__(self, key):
        del self.root[key]

    def __iter__(self):
        return iter(self.root)

    # Modify __contains__ to work correctly when __missing__ is present
    def __contains__(self, key):
        return key in self.root

    # Now, add the methods in dicts but not in MutableMapping
    def __repr__(self):
        return repr(self.root)

    def __or__(self, other):
        if isinstance(other, MappingModel):
            return self.__class__(self.root | other.root)
        if isinstance(other, dict):
            return self.__class__(self.root | other)
        return NotImplemented

    def __ror__(self, other):
        if isinstance(other, MappingModel):
            return self.__class__(other.root | self.root)
        if isinstance(other, dict):
            return self.__class__(other | self.root)
        return NotImplemented

    def __ior__(self, other):
        if isinstance(other, MappingModel):
            self.root |= other.root
        else:
            self.root |= other
        return self

    def __copy__(self):
        inst = self.__class__.__new__(self.__class__)
        inst.__dict__.update(self.__dict__)
        # Create a copy and avoid triggering descriptors
        inst.__dict__["root"] = self.__dict__["root"].copy()
        return inst

    @classmethod
    def fromkeys(cls, iterable, value=None):
        d = cls()
        for key in iterable:
            d[key] = value
        return d


Kind: TypeAlias = Literal["latex", "sympy", "python"]
kinds: list[Kind] = ["latex", "sympy", "python"]


class StrKinds(MappingModel[Kind, str]): ...


ST = TypeVar("ST", bound=StrKinds)
DT = TypeVar("DT", bound=StrKinds)
KindMatch: TypeAlias = tuple[Kind, str]


class Transform(BaseModel, Generic[ST, DT], ABC):
    src: type[ST]
    dst: type[DT]

    @abstractmethod
    def apply(self, src: ST) -> DT: ...


class Defaults(Transform[ST, DT], Generic[ST, DT]):
    name: str = ""

    def apply(self, src: ST) -> DT:
        forms = src.model_copy()
        for kind in kinds:
            if not forms.get(kind):
                forms[kind] = ""
        return self.dst(**forms)


class NameDefaults(Transform[ST, DT], Generic[ST, DT]):
    name: str = ""

    def apply(self, src: ST) -> DT:
        forms = src.model_copy()
        if forms["sympy"] and not forms["latex"]:
            forms["latex"] = forms["sympy"]
        for kind in [k for k, form in forms.items() if not form]:
            forms[kind] = rf"\{self.name}" if kind == "latex" else self.name
        return self.dst(**forms)


class Replacements(Transform[ST, DT], Generic[ST, DT]):
    repls: Mapping[KindMatch, KindMatch] = Field(default_factory=dict)

    def apply(self, src: ST) -> DT:
        forms = src.model_copy()
        for (old_kind, old), (new_kind, new) in self.repls.items():
            forms[new_kind] = forms[old_kind].replace(old, new)
        return self.dst(**forms)


T = TypeVar("T")


class Forms(StrKinds):
    def apply(self, transform: Transform[Any, T]) -> T:  # type: ignore
        return transform.apply(self)


class Param(Forms): ...


class Equation(Forms): ...


class Code(StrKinds): ...


class Expectation(BaseModel, arbitrary_types_allowed=True):
    name: str
    test: float | NDArray[float64]
    expect: float | Sequence[float] | NDArray[float64]
