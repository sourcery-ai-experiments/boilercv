"""Manual data processing stages."""

from pathlib import Path

EQUATIONS = Path("data/equations.toml")
"""Equations TOML file."""
TABLE = "equation"
"""Table name in the equations TOML file."""
SYMPY = "sympy"
"""Key for SymPy expressions in the equations TOML file."""
