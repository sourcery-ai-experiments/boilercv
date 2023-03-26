"""Tools for datasets."""

from collections.abc import Callable, Sequence
from itertools import chain

import numpy as np
import xarray as xr

from boilercv.data.models import Dimension, get_dims
from boilercv.types import DA, DS, ArrLike, Img


def x(da: DA, dim: str, coord: str) -> DA:
    """Return a coordinate from a DataArray."""
    return da.where(da[dim] == coord, drop=True)


def apply_da_frames(func: Callable[[Img], Img], images: xr.DataArray) -> xr.DataArray:
    """Apply functions to each frame of a data array."""
    core_dims = [["ypx", "xpx"]]
    return xr.apply_ufunc(
        func,
        images,
        input_core_dims=core_dims,
        output_core_dims=core_dims,
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
