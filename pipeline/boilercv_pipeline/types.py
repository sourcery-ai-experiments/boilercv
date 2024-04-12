"""Types."""

from collections.abc import Callable
from pathlib import Path
from types import SimpleNamespace
from typing import Literal, TypeAlias

NbProcess: TypeAlias = Callable[[Path, SimpleNamespace], None]
"""Notebook process."""
Stage: TypeAlias = Literal["large_sources", "sources", "filled"]
"""Stage."""
