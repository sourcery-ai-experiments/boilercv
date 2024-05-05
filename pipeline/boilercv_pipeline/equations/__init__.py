"""Equations."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Mapping, Sequence
from pathlib import Path
from shlex import quote
from typing import Any, Generic, Literal, Self, TypeAlias, TypeVar

from numpy import float64
from numpy.typing import NDArray
from pydantic import BaseModel, Field, RootModel, model_validator

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


class KindModel(MappingModel[Kind, str]): ...


ST = TypeVar("ST", bound=KindModel)
DT = TypeVar("DT", bound=KindModel)
KindMatch: TypeAlias = tuple[Kind, str]


class Transform(BaseModel, Generic[ST, DT], ABC):
    src: type[ST]
    dst: type[DT]

    @abstractmethod
    def apply(self, src: ST) -> DT: ...


class Replacements(Transform[ST, DT], Generic[ST, DT]):
    repls: Mapping[KindMatch, KindMatch] = Field(default_factory=dict)

    def apply(self, src: ST) -> DT:
        model = src.model_copy()
        for (old_kind, old), (new_kind, new) in self.repls.items():
            model[new_kind] = model[old_kind].replace(old, new)
        return self.dst(**model)


class Defaults(Transform[ST, DT], Generic[ST, DT]):
    name: str = ""

    def apply(self, src: ST) -> DT:
        model = src.model_copy()
        for kind in kinds:
            if not model.get(kind):
                model[kind] = ""
        if model["sympy"] and not model["latex"]:
            model["latex"] = model["sympy"]
        for kind in [k for k, form in model.items() if not form]:
            model[kind] = rf"\{self.name}" if kind == "latex" else self.name
        return self.dst(**model)


T = TypeVar("T")


class Forms(KindModel):
    def apply(self, transform: Transform[Any, T]) -> T:  # type: ignore
        return transform.apply(self)


class Param(Forms): ...


class Equation(Forms): ...


florschuetz_chao_1965 = Equation({
    "latex": r"\beta = 1 - 4 \\Ja \\sqrt{\\Fo_\\o / \\pi}",
    "sympy": r"Eq(beta, 1 - 4 * Ja * sqrt(Fo_0 / pi))",
    "python": r"1 - 4 * bubble_jakob * sqrt(bubble_fourier / pi)",
})


class Equation(KindModel):
    @model_validator(mode="after")
    def transform(self) -> Self:
        """Set default forms."""
        self.forms.transform(self.transforms)
        forms = self.forms
        for transform in self.transforms:
            value = getattr(forms, transform.src)
            for old, new in transform.repls.items():
                value = value.replace(old, new)
            setattr(forms, transform.dst, value)
        if forms.sympy and not forms.latex:
            forms.latex = forms.sympy
        for field in set(forms.model_fields) - forms.model_fields_set:
            name = rf"\{self.name}" if field == "latex" else self.name
            setattr(self.forms, field, name)
        return self


class Code(KindModel): ...


transforms = Transforms([
    StringReplace(src=kind, dst=kind, repls={"\n": "", "    ": ""})  # pyright: ignore[reportArgumentType]  1.1.360, pydantic 2.4.2
    for kind in ["latex", "sympy", "python"]
])


class Expectation(BaseModel, arbitrary_types_allowed=True):
    name: str
    test: float | NDArray[float64]
    expect: float | Sequence[float] | NDArray[float64]


# class Param(Transformable, arbitrary_types_allowed=True):
#     test: float | NDArray[float64] | None = None

#     @model_validator(mode="after")
#     def transform(self) -> Self:
#         """Set default forms."""
#         self.forms.transform(self.transforms)
#         forms = self.forms
#         for transform in self.transforms:
#             value = getattr(forms, transform.src)
#             for old, new in transform.repls.items():
#                 value = value.replace(old, new)
#             setattr(forms, transform.dst, value)
#         if forms.sympy and not forms.latex:
#             forms.latex = forms.sympy
#         for field in set(forms.model_fields) - forms.model_fields_set:
#             name = rf"\{self.name}" if field == "latex" else self.name
#             setattr(self.forms, field, name)
#         return self
