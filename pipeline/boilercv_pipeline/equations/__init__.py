"""Image process."""

from pathlib import Path
from shlex import quote
from tomllib import loads

from numpy import linspace

MANUAL_SYMPY = ["florschuetz_chao_1965"]
"""Symbolic equations manually encoded so far."""

TOML = Path("data/equations.toml")
"""Equations TOML file."""
PNGS = Path("data/equations")
"""Equation PNGs."""

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

ARGS_ = "arg"
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

_eqs = loads(TOML.read_text("utf-8"))
"""Potentially stale equations TOML data, loaded at module import time."""

ARGS = {arg[SYM]: arg[NAME] for arg in _eqs[ARGS_]}
"""Potential argument set for lambda functions."""
SUBS = {**ARGS, "beta": "dimensionless_bubble_diameter", "pi": "pi"}
"""Substitutions from SymPy symbolic variables to descriptive names."""

KWDS = {
    arg[NAME]: arg[TEST] if isinstance(arg[TEST], float) else linspace(**arg[TEST])
    for arg in _eqs[ARGS_]
}
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
