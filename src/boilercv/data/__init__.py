"""Tools for datasets."""

from collections.abc import Callable, Sequence
from dataclasses import asdict
from itertools import chain
from pathlib import Path

import numpy as np
import xarray as xr
from scipy.spatial.distance import euclidean

from boilercv import (
    HEADER,
    LENGTH_UNITS,
    OTHER_ROI,
    OTHER_ROI_LONG_NAME,
    OTHER_ROI_UNITS,
    ROI,
    ROI_LONG_NAME,
    ROI_UNITS,
    SAMPLE_DIAMETER_UM,
    TIMEZONE,
    VIDEO,
    VIDEO_LONG_NAME,
    VIDEO_UNITS,
)
from boilercv.data.models import Dimension, get_dims
from boilercv.gui import load_roi
from boilercv.models.params import PARAMS
from boilercv.types import DA, DS, ArrInt
from boilercv.video.cine import get_cine_attributes, get_cine_images


def apply_to_frames(
    func: Callable[[ArrInt], ArrInt], images: xr.DataArray
) -> xr.DataArray:
    """Apply functions to each frame of a data array."""
    core_dims = [["ypx", "xpx"]]
    return xr.apply_ufunc(
        func,
        images,
        input_core_dims=core_dims,
        output_core_dims=core_dims,
        vectorize=True,
    )


def assign_to_dataset(
    name: str,
    data: ArrInt | Sequence[ArrInt],
    dims: list[Dimension] | tuple[Dimension, ...],
    ds: DS | None = None,
    secondary_dims: list[Dimension] | tuple[Dimension, ...] = (),
    long_name: str = "",
    units: str = "",
) -> DS:
    """Build a DataArray."""
    if not ds:
        ds = xr.Dataset()
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
    ds[name] = da
    return ds


# * -------------------------------------------------------------------------------- * #
# * PRIMARY DATASET


def prepare_dataset(
    cine_source: Path, num_frames: int | None = None, start_frame: int = 0
) -> DS:
    """Prepare a dataset from a CINE."""
    header, utc_arr = get_cine_attributes(
        cine_source, TIMEZONE, num_frames, start_frame
    )
    header_da = xr.DataArray(name=HEADER, attrs=asdict(header))
    frames = Dimension(dim="frame", long_name="Frame number")
    ypx = Dimension(dim="ypx", long_name="Height", units="px")
    xpx = Dimension(dim="xpx", long_name="Width", units="px")
    time = Dimension(
        parent_dim=frames.dim,
        dim="time",
        long_name="Time elapsed",
        units="s",
        original_units="ns",
        original_coords=(utc_arr - utc_arr[0]).astype(float),
        scale=1e-9,
    )
    utc = Dimension(
        parent_dim=frames.dim,
        dim="utc",
        long_name="UTC time",
        coords=utc_arr,
    )
    ds = assign_to_dataset(
        name=VIDEO,
        long_name=VIDEO_LONG_NAME,
        units=VIDEO_UNITS,
        dims=(frames, ypx, xpx),
        secondary_dims=(time, utc),
        data=list(get_cine_images(cine_source, num_frames, start_frame)),
    )
    ds[header_da.name] = header_da
    return ds


def assign_length_scales(dataset: DS) -> DS:
    """Assign length scales to "x" and "y" coordinates."""
    images = dataset[VIDEO]
    parent_dim_units = "px"
    roi = load_roi(images.data, PARAMS.paths.examples / "roi_line.yaml", "line")
    pixels = euclidean(*iter(roi))
    um_per_px = SAMPLE_DIAMETER_UM / pixels
    y = get_length_scale(parent_dim_units, "y", "Height", um_per_px, images)
    x = get_length_scale(parent_dim_units, "x", "Width", um_per_px, images)
    images = y.assign_to(images)
    images = x.assign_to(images)
    return dataset


def get_length_scale(
    parent_dim_units: str, dim: str, long_name: str, scale: float, images: DA
) -> Dimension:
    """Get a length scale."""
    parent_dim = f"{dim}{parent_dim_units}"
    return Dimension(
        parent_dim=f"{dim}{parent_dim_units}",
        dim=dim,
        long_name=long_name,
        units=LENGTH_UNITS,
        original_units=parent_dim_units,
        original_coords=images[parent_dim].values,
        scale=scale,
    )


# * -------------------------------------------------------------------------------- * #
# * CONTOURS

X_Y_COORDS = ["xpx", "ypx"]


def assign_roi_to_dataset(ds: DS, roi_contour: ArrInt) -> DS:
    """Pack a contour into a DataArray."""

    return assign_to_dataset(
        ds=ds,
        name=ROI,
        long_name=ROI_LONG_NAME,
        units=ROI_UNITS,
        dims=(
            Dimension(dim="roi_vertex", long_name="ROI vertex"),
            Dimension(
                dim="roi_loc",
                long_name="ROI vertex location",
                coords=X_Y_COORDS,
            ),
        ),
        data=roi_contour,
    )


def assign_other_roi_to_dataset(ds: DS, contours: list[ArrInt]) -> DS:
    """Pack a contour into a DataArray."""
    return assign_to_dataset(
        ds=ds,
        name=OTHER_ROI,
        long_name=OTHER_ROI_LONG_NAME,
        units=OTHER_ROI_UNITS,
        dims=(
            Dimension(dim="contour", long_name="Extra contour"),
            Dimension(dim="contour_vertex", long_name="Extra contour vertex"),
            Dimension(
                dim="contour_loc",
                long_name="Contour vertex location",
                coords=X_Y_COORDS,
            ),
        ),
        data=contours,
    )
