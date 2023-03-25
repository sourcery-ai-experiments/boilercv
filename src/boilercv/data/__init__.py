"""Tools for datasets."""

from collections.abc import Callable
from dataclasses import asdict
from pathlib import Path

import xarray as xr
from scipy.spatial.distance import euclidean

from boilercv import HEADER, LENGTH_UNITS, SAMPLE_DIAMETER_UM, TIMEZONE, VIDEO
from boilercv.data.models import UnitScale
from boilercv.gui import load_roi
from boilercv.models.params import PARAMS
from boilercv.types import ArrInt
from boilercv.video.cine import get_cine_attributes, get_cine_images

# TODO: Broaden type hints to take any parameters, since it won't have just one arg


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


def prepare_dataset(
    cine_source: Path, num_frames: int | None = None, start_frame: int = 0
) -> xr.Dataset:
    """Prepare a dataset from a CINE."""
    header_, utc_ = get_cine_attributes(cine_source, TIMEZONE, num_frames, start_frame)
    header = xr.DataArray(name=HEADER, attrs=asdict(header_))
    frames = UnitScale(dim="frames", long_name="Frame number")
    time = UnitScale(
        parent_dim=frames.dim,
        dim="time",
        long_name="Time elapsed",
        units="s",
        original_units="ns",
        original_coords=(utc_ - utc_[0]).astype(float),
        scale=1e-9,
    )
    utc = UnitScale(
        parent_dim=frames.dim,
        dim="utc",
        long_name="UTC time",
        coords=utc_,
    )
    ypx = UnitScale(dim="ypx", long_name="Height", units="px")
    xpx = UnitScale(dim="xpx", long_name="Width", units="px")
    images = xr.DataArray(
        name=VIDEO,
        dims=(frames.dim, ypx.dim, xpx.dim),
        data=list(get_cine_images(cine_source, num_frames, start_frame)),
        attrs=dict(long_name="High-speed video data", units="Intensity"),
    )
    for coord in (time, utc, ypx, xpx):
        images = coord.assign_to(images)
    return xr.Dataset({images.name: images, header.name: header})


def assign_length_scales(dataset: xr.Dataset) -> xr.Dataset:
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
    parent_dim_units: str, dim: str, long_name: str, scale: float, images: xr.DataArray
) -> UnitScale:
    """Get a length scale."""
    parent_dim = f"{dim}{parent_dim_units}"
    return UnitScale(
        parent_dim=f"{dim}{parent_dim_units}",
        dim=dim,
        long_name=long_name,
        units=LENGTH_UNITS,
        original_units=parent_dim_units,
        original_coords=images[parent_dim].values,
        scale=scale,
    )
