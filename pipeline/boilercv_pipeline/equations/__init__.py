"""Equations."""

from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from shlex import quote

EQS = "equation"
"""Equations table name in the equations TOML file."""
NAME = "name"
"""Key for equation names in the equations TOML file."""
LATEX = "latex"
"""Key for LaTeX expressions in the equations TOML file."""
SYMPY = "sympy"
"""Key for SymPy expressions in the equations TOML file."""
PYTHON = "python"
"""Key for Python functions in the equations TOML file."""
EXPECT = "expect"
"""Key for expected values in the equations TOML file."""

ARGS = "arg"
"""Equation arguments table name in the equations TOML file."""
SYM = "sym"
"""Key for symbolic variable names in the equation arguments table."""
TEST = "test"
"""Key for test values in the equation arguments table."""

PIPX = quote((Path(".venv") / "scripts" / "pipx").as_posix())
"""Escaped path to `pipx` executable suitable for `subprocess.run` invocation."""
INDEX = "https://download.pytorch.org/whl/cu121"
"""Extra index URL for PyTorch and CUDA dependencies."""
PNG_PARSER = quote((Path("scripts") / "convert_png_to_latex.py").as_posix())
"""Escaped path to converter script suitable for `subprocess.run` invocation."""
LATEX_PARSER = (Path("scripts") / "convert_latex_to_sympy.py").as_posix()
"""Escaped path to parser script suitable for `subprocess.run` invocation."""

SYMPY_REPL = {"{o}": "0", "{bo}": "b0"}
"""Replacements after parsing LaTeX to SymPy."""
TOML_REPL = {'"\n\n': "\n'''\n\n", '"\n': "\n'''\n", ' "': " '''\n", r"\\": "\\"}
"""Replacements to make to raw TOML just prior to serialization."""
LATEX_REPL = {"{0}": r"\o", "{b0}": r"\b0"}
"""Replacements to make after parsing LaTeX from PNGs."""


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
    source: Equation
    destination: Equation


@dataclass
class Param:
    """Param."""

    name: str
    arg: bool = False
    sym: str = ""
    test: float | None = None
