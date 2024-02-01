"""Types relevant to array manipulation and image processing."""

from typing import Any, Protocol, TypeAlias, TypeVar

import numpy as np
import pandas as pd
import xarray as xr
from numpy import typing as npt

DF: TypeAlias = pd.DataFrame
DA: TypeAlias = xr.DataArray
DS: TypeAlias = xr.Dataset
DfOrS: TypeAlias = pd.DataFrame | pd.Series  # type: ignore  # pyright 1.1.333

DA_T = TypeVar("DA_T", bound=DA)


class SupportsMul(Protocol):
    """Protocol for types that support multiplication."""

    def __mul__(self, other: Any) -> Any:
        ...


SupportsMul_T = TypeVar("SupportsMul_T", bound=SupportsMul)

ArrLike: TypeAlias = npt.ArrayLike

NBit: TypeAlias = npt.NBitBase
"""A number with arbitrary precision."""

Arr: TypeAlias = npt.NDArray[np.generic]
"""Generic array type. Consistent with OpenCV's type annotations."""

ArrBool: TypeAlias = npt.NDArray[np.bool_]
"""A boolean array."""

ArrFloat: TypeAlias = npt.NDArray[np.floating[NBit]]
"""An integer array with arbitrary bit depth."""

ArrInt: TypeAlias = npt.NDArray[np.integer[NBit]]
"""An integer array."""

ArrNum: TypeAlias = npt.NDArray[np.number[NBit]]
"""A number array."""

ArrDT: TypeAlias = npt.NDArray[np.datetime64]
"""Datetime array type."""

ArrTD: TypeAlias = npt.NDArray[np.timedelta64]
"""Timedelta array type."""

Img: TypeAlias = ArrInt
"""An integer array representing an image."""

ImgBool: TypeAlias = ArrBool
"""A boolean array representing an image mask."""

ImgLike: TypeAlias = ArrLike
"""An array-like object representable as an image."""

Vid: TypeAlias = Img
"""An integer array representing a video."""

VidBool: TypeAlias = ImgBool
"""A boolean array representing a video mask."""

Float: TypeAlias = ArrFloat | float
"""A scalar number or number array."""

Int: TypeAlias = ArrInt | int
"""A scalar number or integer number array."""
