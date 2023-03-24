"""Base types on which other types are built."""

from typing import TypeAlias, TypeVar

import numpy as np
from numpy import typing as npt
from numpy._typing import _8Bit, _16Bit, _32Bit, _64Bit

# * -------------------------------------------------------------------------------- * #

NBit: TypeAlias = npt.NBitBase

NBit_T = TypeVar("NBit_T", bound=NBit)
"""A number with arbitrary precision."""

# * -------------------------------------------------------------------------------- * #

ArrFloat: TypeAlias = npt.NDArray[np.floating[NBit_T]]
"""An integer array with arbitrary bit depth."""

ArrFloat8: TypeAlias = ArrFloat[_8Bit]
"""An integer array with 64-bit depth."""

ArrFloat16: TypeAlias = ArrFloat[_16Bit]
"""An integer array with 64-bit depth."""

ArrFloat32: TypeAlias = ArrFloat[_32Bit]
"""An integer array with 64-bit depth."""

ArrFloat64: TypeAlias = ArrFloat[_64Bit]
"""An integer array with 64-bit depth."""

# * -------------------------------------------------------------------------------- * #

ArrInt: TypeAlias = npt.NDArray[np.integer[NBit_T]]
"""An integer array with arbitrary bit depth."""

ArrInt8: TypeAlias = ArrInt[_8Bit]
"""An integer array with 8-bit depth."""

ArrInt16: TypeAlias = ArrInt[_16Bit]
"""An integer array with 16-bit depth."""

ArrInt32: TypeAlias = ArrInt[_32Bit]
"""An integer array with 32-bit depth."""

ArrInt64: TypeAlias = ArrInt[_64Bit]
"""An integer array with 64-bit depth."""

# * -------------------------------------------------------------------------------- * #

Img: TypeAlias = ArrInt[NBit_T]
"""An image with arbitrary bit depth."""

Img16: TypeAlias = ArrInt[_16Bit]
"""An image with 16-bit depth."""

Img32: TypeAlias = ArrInt[_32Bit]
"""An image with 32-bit depth."""

Img64: TypeAlias = ArrInt[_64Bit]
"""An image with 64-bit depth."""

# * -------------------------------------------------------------------------------- * #

ImgSeq = list[Img[NBit_T]]
"""A sequence of images."""

ImgSeq16: TypeAlias = ImgSeq[_16Bit]
"""An image sequence with 16-bit depth."""

ImgSeq32: TypeAlias = ImgSeq[_32Bit]
"""An image sequence with 32-bit depth."""

ImgSeq64: TypeAlias = ImgSeq[_64Bit]
"""An image sequence with 64-bit depth."""

# * -------------------------------------------------------------------------------- * #

_8Bit_T = TypeVar("_8Bit_T", bound=_8Bit)
"""A number with 8-bit precision."""

_16Bit_T = TypeVar("_16Bit_T", bound=_16Bit)
"""A number with 16-bit precision."""

_32Bit_T = TypeVar("_32Bit_T", bound=_32Bit)
"""A number with 32-bit precision."""

_64Bit_T = TypeVar("_64Bit_T", bound=_32Bit)
"""A number with 64-bit precision."""
