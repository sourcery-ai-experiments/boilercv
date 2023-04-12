"""Tools for datasets."""

from collections.abc import Callable, Sequence
from itertools import chain
from typing import Any

import numpy as np
import pandas as pd
import xarray as xr
from pytz import timezone

from boilercv.data.models import Dimension, get_dims
from boilercv.types import DA, DS, ArrLike

VIDEO = "video"
ROI = "roi"
HEADER = "header"
TIMEZONE = timezone("US/Pacific")

FRAME = "frame"
TIME = "time"
UTC_TIME = "utc"

Y = "y"
X = "x"
YX = ["y", "x"]

PX = "px"
YPX = f"{Y}{PX}"
XPX = f"{X}{PX}"
YX_PX = [YPX, XPX]

DIMS = [FRAME, YPX, XPX]

PACKED_DIM_INDEX = 2
PACKED = "packed"
XPX_PACKED = "xpx_packed"
PACKED_DIMS = [FRAME, YPX, XPX_PACKED]

VIDEO_NAME = "video_name"

LENGTH = "um"
SAMPLE_DIAMETER_UM = 9_525_000
ROI = "roi"
OTHER_ROI = "roi_other"

IDX = pd.IndexSlice
"""Helper for slicing multi-index dataframes."""


def identity_da(da: DA, dim: str) -> DA:
    """Construct a data array that maps a dimension's coordinates to itself.

    Useful to apply `xr.apply_ufunc` along coordinate values.

    Args:
        da: Data array.
        dim: The dimension to extract.
    """
    return xr.DataArray(
        dims=(dim),
        coords={dim: da[dim].values},
        data=da[dim],
    )


def apply_to_img_da(
    func: Callable[..., Any],
    *args: Any,
    returns: int | None = 1,
    vectorize: bool = False,
    name: Sequence[str] | str = "",
    kwargs: dict[str, Any] | None = None,
) -> Any:
    """Apply functions that transform images to transform data arrays instead."""
    core_dims = [YX_PX]
    common_kwargs = dict(
        input_core_dims=core_dims * len(args),
        vectorize=vectorize,
        keep_attrs=True,
        kwargs=kwargs,
    )
    if returns and returns > 0:
        result = xr.apply_ufunc(
            func,
            *args,
            **common_kwargs,
            output_core_dims=core_dims * returns,
        )
        if name and returns == 1:
            result = result.rename(name)
        if name and returns > 1:
            result = tuple(
                part.rename(name_) for name_, part in zip(name, result, strict=True)
            )
        return result
    if not returns or returns == 0:
        xr.apply_ufunc(
            func,
            *args,
            **common_kwargs,
        )


def assign_ds(
    name: str,
    data: ArrLike,
    dims: Sequence[Dimension],
    secondary_dims: Sequence[Dimension] = (),
    fixed_dims: Sequence[Dimension] = (),
    fixed_secondary_dims: Sequence[Dimension] = (),
    ds: DS | None = None,
    long_name: str = "",
    units: str = "",
) -> DS:
    """Build a data array and assign it to a dataset."""
    if not ds:
        ds = xr.Dataset()
    da = build_da(
        name,
        data,
        dims,
        secondary_dims,
        fixed_dims,
        fixed_secondary_dims,
        long_name,
        units,
    )
    ds[name] = da
    return ds


def build_da(
    name: str,
    data: ArrLike,
    dims: Sequence[Dimension],
    secondary_dims: Sequence[Dimension] = (),
    fixed_dims: Sequence[Dimension] = (),
    fixed_secondary_dims: Sequence[Dimension] = (),
    long_name: str = "",
    units: str = "",
):
    """Build a data array."""
    all_primary_dims = chain(fixed_dims, dims)
    all_fixed_dims = chain(fixed_dims, fixed_secondary_dims)
    all_variable_dims = chain(dims, secondary_dims)
    if not long_name:
        long_name = name.capitalize() if len(name) > 1 else name
    if isinstance(data, Sequence) and not len(data):
        shape: list[int] = []
        for dim in all_primary_dims:
            if dim.coords is None:
                shape.append(1)
            else:
                shape.append(len(dim.coords))
        data = np.full(shape, None)
    attrs = {"long_name": long_name}
    if units:
        attrs["units"] = units
    da = xr.DataArray(
        name=name,
        dims=get_dims(*all_primary_dims),
        data=data,
        attrs=attrs,
    )
    for dim in chain(all_fixed_dims, all_variable_dims):
        da = dim.assign_to(da)
    return da
