"""Image process."""

from pathlib import Path
from shlex import quote

EQUATIONS = Path("data/equations.toml")
"""Equations TOML file."""
PNGS = Path("data/equations")
"""Equation PNGs."""
TABLE = "equation"
"""Table name in the equations TOML file."""
LATEX = "latex"
"""Key for LaTeX expressions in the equations TOML file."""
SYMPY = "sympy"
"""Key for SymPy expressions in the equations TOML file."""
PIPX = quote((Path(".venv") / "scripts" / "pipx").as_posix())
"""Escaped path to `pipx` executable suitable for `subprocess.run` invocation."""
POST_REPL = {'"\n\n': "\n'''\n\n", '"\n': "\n'''\n", ' "': " '''\n", r"\\": "\\"}
"""Replacements to make just before serialization."""
