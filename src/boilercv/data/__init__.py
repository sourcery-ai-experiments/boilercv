"""Tools for datasets."""

from collections.abc import Callable, Sequence
from itertools import chain
from typing import Any

import numpy as np
import xarray as xr
from pytz import timezone

from boilercv.data.models import Dimension, get_dims
from boilercv.types import DS, ArrLike

TIMEZONE = timezone("US/Pacific")
VIDEO = "video"
HEADER = "header"
DIMS = ["y", "x"]
LENGTH = "um"
PX = "px"
PX_DIMS = [f"{dim}{PX}" for dim in DIMS]
ROI = "roi"
OTHER_ROI = "roi_other"
SAMPLE_DIAMETER_UM = 9_525_000


def apply_to_img_da(
    func: Callable[..., Any],
    func_image_args: Any,
    returns: int | None = 1,
    vectorize: bool = False,
    name: Sequence[str] | str = "",
    kwargs: dict[str, Any] | None = None,
) -> Any:
    """Apply functions that transform images to transform data arrays instead."""
    core_dims = [PX_DIMS]
    if isinstance(func_image_args, xr.DataArray):
        func_image_args = (func_image_args,)
    common_kwargs = dict(
        input_core_dims=core_dims * len(func_image_args),
        vectorize=vectorize,
        kwargs=kwargs,
    )
    if returns and returns > 0:
        result = xr.apply_ufunc(
            func,
            *func_image_args,
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
            *func_image_args,
            **common_kwargs,
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
