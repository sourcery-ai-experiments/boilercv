"""Number container types, including images."""

from typing import TypeAlias, TypeVar

from numpy import typing as npt
import numpy as np
from numpy._typing import _8Bit  # pyright: ignore[reportPrivateUsage]

NBit: TypeAlias = npt.NBitBase

NBit_T = TypeVar("NBit_T", bound=NBit)
"""Represents a number with arbitrary precision."""

Img: TypeAlias = npt.NDArray[np.integer[NBit_T]]
"""An image parametrized on its bit depth."""

Img8Bit: TypeAlias = npt.NDArray[np.integer[_8Bit]]
"""An image with 8-bit depth."""
