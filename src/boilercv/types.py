"""Types relevant to array manipulation and image processing."""

from typing import Any, Protocol, TypeAlias, TypeVar

from numpy import bool_, datetime64, floating, generic, integer, number, timedelta64
from numpy.typing import ArrayLike, NBitBase, NDArray
from pandas import DataFrame, Series
from xarray import DataArray, Dataset

DF: TypeAlias = DataFrame
DA: TypeAlias = DataArray
DS: TypeAlias = Dataset
DfOrS: TypeAlias = DataFrame | Series  # type: ignore  # pyright 1.1.333

DA_T = TypeVar("DA_T", bound=DA)


class SupportsMul(Protocol):
    """Protocol for types that support multiplication."""

    def __mul__(self, other: Any) -> Any: ...


SupportsMul_T = TypeVar("SupportsMul_T", bound=SupportsMul)

ArrLike: TypeAlias = ArrayLike

NBit: TypeAlias = NBitBase
"""A number with arbitrary precision."""

Arr: TypeAlias = NDArray[generic]
"""Generic array type. Consistent with OpenCV's type annotations."""

ArrBool: TypeAlias = NDArray[bool_]
"""A boolean array."""

ArrFloat: TypeAlias = NDArray[floating[NBit]]
"""An integer array with arbitrary bit depth."""

ArrInt: TypeAlias = NDArray[integer[NBit]]
"""An integer array."""

ArrNum: TypeAlias = NDArray[number[NBit]]
"""A number array."""

ArrDT: TypeAlias = NDArray[datetime64]
"""Datetime array type."""

ArrTD: TypeAlias = NDArray[timedelta64]
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
