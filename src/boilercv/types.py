"""Types relevant to array manipulation and image processing."""

from typing import Any, Protocol, TypeAlias, TypeVar

import numpy as np
from numpy import typing as npt


class SupportsMul(Protocol):
    """Protocol for types that support multiplication."""

    def __mul__(self, other: Any) -> Any:
        ...


SupportsMul_T = TypeVar("SupportsMul_T", bound=SupportsMul)

NBit: TypeAlias = npt.NBitBase
"""A number with arbitrary precision."""

ArrInt: TypeAlias = npt.NDArray[np.integer[NBit]]
"""An integer array with arbitrary bit depth."""

ArrFloat: TypeAlias = npt.NDArray[np.floating[NBit]]
"""An integer array with arbitrary bit depth."""

ArrGen: TypeAlias = npt.NDArray[np.generic]
"""Generic array type. Consistent with OpenCV's type annotations."""

ArrDT: TypeAlias = npt.NDArray[np.datetime64]
"""Datetime array type."""

ArrTD: TypeAlias = npt.NDArray[np.timedelta64]
"""Timedelta array type."""
