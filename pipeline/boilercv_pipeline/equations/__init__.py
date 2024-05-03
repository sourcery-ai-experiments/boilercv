"""Equations."""

from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from shlex import quote
from typing import Literal

import numpy as np
from numpy.typing import NDArray

PIPX = quote((Path(".venv") / "scripts" / "pipx").as_posix())
"""Escaped path to `pipx` executable suitable for `subprocess.run` invocation."""
INDEX = "https://download.pytorch.org/whl/cu121"
"""Extra index URL for PyTorch and CUDA dependencies."""
PNG_PARSER = quote((Path("scripts") / "convert_png_to_latex.py").as_posix())
"""Escaped path to converter script suitable for `subprocess.run` invocation."""
LATEX_PARSER = (Path("scripts") / "convert_latex_to_sympy.py").as_posix()
"""Escaped path to parser script suitable for `subprocess.run` invocation."""


FormKind = Literal["latex", "sympy", "python"]
"""Equation form kind."""


@dataclass
class Forms:
    """Forms."""

    latex: str = ""
    sympy: str = ""
    python: str = ""


@dataclass
class Equation:
    """Equation."""

    name: str
    forms: Forms
    expect: list[float]


@dataclass
class Transform:
    """Transform."""

    transform: Callable[[str], str]
    src: FormKind
    dst: FormKind


@dataclass
class Equations:
    """Equations."""

    equations: dict[str, Equation]


# TODO: Post-process forms to replace missing ones with `name`


@dataclass
class LinspaceKwds:
    """Keyword arguments to `numpy.linspace`."""

    start: float
    stop: float
    num: int


@dataclass
class Param:
    """Param."""

    name: str
    forms: Forms = field(default_factory=Forms)
    test: float | NDArray[np.float64] | None = None
