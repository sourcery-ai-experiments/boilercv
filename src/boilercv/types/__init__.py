"""Types relevant to array manipulation and image processing."""

from typing import Any, Protocol, TypeAlias, TypeVar

import numpy as np
from numpy import typing as npt
from numpy._typing import _8Bit

from boilercv.types.base import ArrFloat64, ArrInt, ArrInt8, ArrInt32, ImgSeq


class SupportsMul(Protocol):
    """Protocol for types that support multiplication."""

    def __mul__(self, other: Any) -> Any:
        ...


SupportsMul_T = TypeVar("SupportsMul_T", bound=SupportsMul)


# * -------------------------------------------------------------------------------- * #

ArrGen: TypeAlias = npt.NDArray[np.generic]
"""Generic array type. Consistent with OpenCV's type annotations."""

ArrDatetime: TypeAlias = npt.NDArray[np.datetime64]
"""Datetime array type."""

ArrTimeDelta: TypeAlias = npt.NDArray[np.timedelta64]
"""Timedelta array type."""

ArrBool8: TypeAlias = ArrInt8
"""An array with 8-bit boolean depth."""

ArrIntDef: TypeAlias = ArrInt32
"""The default integer array type on Windows."""

ArrFloatDef: TypeAlias = ArrFloat64
"""The default float array type on most modern machines."""

# * -------------------------------------------------------------------------------- * #

Img8: TypeAlias = ArrInt[_8Bit]
"""An image with 8-bit depth."""

ImgBool8: TypeAlias = ArrBool8
"""An image with 8-bit boolean depth."""

# * -------------------------------------------------------------------------------- * #

ImgSeq8: TypeAlias = ImgSeq[_8Bit]
"""An image sequence with 8-bit depth."""
