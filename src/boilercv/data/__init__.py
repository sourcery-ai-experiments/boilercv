"""Tools for datasets."""

from collections.abc import Callable, Sequence
from itertools import chain

import numpy as np
import xarray as xr
from pytz import timezone

from boilercv.data.models import Dimension, get_dims
from boilercv.types import DS, ArrLike, Img

TIMEZONE = timezone("US/Pacific")
VIDEO = "video"
HEADER = "header"
LENGTH_DIMS = ["y", "x"]
LENGTH_UNITS = "um"
PRIMARY_LENGTH_UNITS = "px"
PRIMARY_LENGTH_DIMS = [f"{dim}{PRIMARY_LENGTH_UNITS}" for dim in LENGTH_DIMS]
ROI = "roi"
OTHER_ROI = "roi_other"
SAMPLE_DIAMETER_UM = 9_525_000


def apply_to_frames(
    func: Callable[[Img], Img], images: xr.DataArray, returns: int = 1
) -> xr.DataArray:
    """Apply functions to each frame of a data array."""
    core_dims = [PRIMARY_LENGTH_DIMS]
    return xr.apply_ufunc(
        func,
        images,
        input_core_dims=core_dims,
        output_core_dims=core_dims * returns,
        vectorize=True,
    )


def assign_ds(
    name: str,
    data: ArrLike,
    dims: list[Dimension] | tuple[Dimension, ...],
    ds: DS | None = None,
    secondary_dims: list[Dimension] | tuple[Dimension, ...] = (),
    long_name: str = "",
    units: str = "",
) -> DS:
    """Build a data array and assign it to a dataset."""
    if not ds:
        ds = xr.Dataset()
    da = build_da(name, data, dims, secondary_dims, long_name, units)
    ds[name] = da
    return ds


def build_da(
    name: str,
    data: ArrLike,
    dims: list[Dimension] | tuple[Dimension, ...],
    secondary_dims: list[Dimension] | tuple[Dimension, ...] = (),
    long_name: str = "",
    units: str = "",
):
    """Build a data array."""
    if not long_name:
        long_name = name.capitalize() if len(name) > 1 else name
    if isinstance(data, Sequence) and not len(data):
        shape: list[int] = []
        for dim in dims:
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
        dims=get_dims(*dims),
        data=data,
        attrs=attrs,
    )
    for dim in chain(dims, secondary_dims):
        da = dim.assign_to(da)
    return da
