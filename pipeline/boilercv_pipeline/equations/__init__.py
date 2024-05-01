"""Image process."""

from pathlib import Path
from shlex import quote

EQUATIONS = Path("data/equations.toml")
"""Equations TOML file."""
PNGS = Path("data/equations")
"""Equation PNGs."""

TABLE = "equation"
"""Table name in the equations TOML file."""
NAME = "name"
"""Key for equation names in the equations TOML file."""
LATEX = "latex"
"""Key for LaTeX expressions in the equations TOML file."""
SYMPY = "sympy"
"""Key for SymPy expressions in the equations TOML file."""
PYTHON = "python"
"""Key for Python functions in the equations TOML file."""

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

ARGS = {
    "Fo_0": "bubble_fourier",
    "Re_b0": "bubble_initial_reynolds",
    "Ja": "bubble_jakob",
    "Pr": "liquid_prandtl",
}
"""Potential argument set for lambda functions."""
SUBS = {**ARGS, "beta": "dimensionless_bubble_diameter", "pi": "pi"}
"""Substitutions from SymPy symbolic variables to descriptive names."""
