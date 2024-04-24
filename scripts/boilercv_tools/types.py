"""Types."""

from typing import Literal, TypeAlias

Platform: TypeAlias = Literal["linux", "macos", "windows"]
"""Platform."""
Version: TypeAlias = Literal["3.9", "3.10", "3.11", "3.12"]
"""Python version."""
