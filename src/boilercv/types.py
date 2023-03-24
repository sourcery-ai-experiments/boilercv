"""Number container types, including images."""

from typing import Any, Protocol, TypeAlias, TypeVar

import numpy as np
from numpy import typing as npt
from numpy._typing import _8Bit, _16Bit, _32Bit, _64Bit

ArrGen: TypeAlias = npt.NDArray[np.generic]
"""Generic array type. Consistent with OpenCV's type annotations."""

ArrDatetime = npt.NDArray[np.datetime64]
"""Datetime array type."""

NBit: TypeAlias = npt.NBitBase

NBit_T = TypeVar("NBit_T", bound=NBit)
"""A number with arbitrary precision."""

_8Bit_T = TypeVar("_8Bit_T", bound=_8Bit)
"""A number with 8-bit precision."""

_16Bit_T = TypeVar("_16Bit_T", bound=_16Bit)
"""A number with 16-bit precision."""

_32Bit_T = TypeVar("_32Bit_T", bound=_32Bit)
"""A number with 32-bit precision."""

_64Bit_T = TypeVar("_64Bit_T", bound=_32Bit)
"""A number with 64-bit precision."""

ArrFloat: TypeAlias = npt.NDArray[np.floating[NBit_T]]
"""An integer array with arbitrary bit depth."""

ArrFloat64: TypeAlias = ArrFloat[_64Bit]
"""An integer array with 64-bit depth."""

ArrInt: TypeAlias = npt.NDArray[np.integer[NBit_T]]
"""An integer array with arbitrary bit depth."""

ArrInt8: TypeAlias = ArrInt[_8Bit]
"""An integer array with 8-bit depth."""

ArrBool8: TypeAlias = ArrInt8
"""An array with 8-bit boolean depth."""

ArrInt16: TypeAlias = ArrInt[_16Bit]
"""An integer array with 16-bit depth."""

ArrInt32: TypeAlias = ArrInt[_32Bit]
"""An integer array with 32-bit depth."""

ArrInt64: TypeAlias = ArrInt[_64Bit]
"""An integer array with 64-bit depth."""

ArrIntDef: TypeAlias = ArrInt32
"""The default integer array type."""

Img: TypeAlias = ArrInt[NBit_T]
"""An image with arbitrary bit depth."""

ImgBool8: TypeAlias = ArrBool8
"""An image with 8-bit boolean depth."""

Img8: TypeAlias = ArrInt[_8Bit]
"""An image with 8-bit depth."""

Img16: TypeAlias = ArrInt[_16Bit]
"""An image with 16-bit depth."""

Img32: TypeAlias = ArrInt[_32Bit]
"""An image with 32-bit depth."""

Img64: TypeAlias = ArrInt[_64Bit]
"""An image with 64-bit depth."""

ImgSeq = list[Img[NBit_T]]
"""A sequence of images."""

ImgSeq8: TypeAlias = ImgSeq[_8Bit]
"""An image sequence with 8-bit depth."""

ImgSeq16: TypeAlias = ImgSeq[_16Bit]
"""An image sequence with 16-bit depth."""

ImgSeq32: TypeAlias = ImgSeq[_32Bit]
"""An image sequence with 32-bit depth."""

ImgSeq64: TypeAlias = ImgSeq[_64Bit]
"""An image sequence with 64-bit depth."""


class SupportsMul(Protocol):
    """Protocol for types that support multiplication."""

    def __mul__(self, other: Any) -> Any:
        ...


SupportsMul_T = TypeVar("SupportsMul_T", bound=SupportsMul)
