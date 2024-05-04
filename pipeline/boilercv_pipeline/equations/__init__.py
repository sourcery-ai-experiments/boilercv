"""Equations."""

from collections.abc import Mapping, Sequence
from pathlib import Path
from shlex import quote
from typing import Literal, Self

from numpy import float64
from numpy.typing import NDArray
from pydantic import BaseModel, Field, model_validator

PIPX = quote((Path(".venv") / "scripts" / "pipx").as_posix())
"""Escaped path to `pipx` executable suitable for `subprocess.run` invocation."""

FormKind = Literal["latex", "sympy", "python"]
"""Equation form kind."""


class Transform(BaseModel):
    src: FormKind
    dst: FormKind
    repls: Mapping[str, str]


class Forms(BaseModel):
    latex: str = ""
    sympy: str = ""
    python: str = ""

    def transform(self, transforms: Sequence[Transform]) -> Self:
        """Set default forms."""
        for transform in transforms:
            value = getattr(self, transform.src)
            for old, new in transform.repls.items():
                value = value.replace(old, new)
            setattr(self, transform.dst, value)
        return self


class Transformable(BaseModel):
    name: str
    forms: Forms = Field(default_factory=Forms)
    transforms: Sequence[Transform] = Field(default_factory=list)


class Equation(Transformable):
    @model_validator(mode="after")
    def transform(self) -> Self:
        """Set default forms."""
        self.forms.transform(self.transforms)
        return self


class Param(Transformable, arbitrary_types_allowed=True):
    test: float | NDArray[float64] | None = None

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


class Expectation(BaseModel, arbitrary_types_allowed=True):
    name: str
    test: float | NDArray[float64]
    expect: float | Sequence[float] | NDArray[float64]
