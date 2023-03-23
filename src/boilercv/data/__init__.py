"""Tools for datasets."""

from pathlib import Path

import xarray as xr
from scipy.spatial.distance import euclidean

from boilercv import LENGTH_UNITS, SAMPLE_DIAMETER_UM, TIMEZONE
from boilercv.data.models import UnitScale
from boilercv.images import load_roi
from boilercv.models.params import PARAMS
from boilercv.video.cine import get_cine_attributes, get_cine_images
from boilercv.video.cine.models import FlatHeaderStudySpecific


def prepare_images(
    cine_source: Path, num_frames: int | None = None, start_frame: int = 0
) -> tuple[xr.DataArray, FlatHeaderStudySpecific]:
    """Load images from a CINE to an xr.DataArray."""
    variable_name = "images"
    cine_header, utc_ = get_cine_attributes(
        cine_source, TIMEZONE, num_frames, start_frame
    )
    time = UnitScale(
        dim="time",
        long_name="Time elapsed",
        units="s",
        original_units="ns",
        original_coords=(utc_ - utc_[0]).astype(float),
        scale=1e-9,
    )
    utc = UnitScale(
        parent_dim=time.dim,
        dim="utc",
        long_name="UTC time",
        coords=utc_,
    )
    ypx = UnitScale(dim="ypx", long_name="Height", units="px")
    xpx = UnitScale(dim="xpx", long_name="Width", units="px")
    images = xr.DataArray(
        name=variable_name,
        dims=(time.dim, ypx.dim, xpx.dim),
        data=list(get_cine_images(cine_source, num_frames, start_frame)),
        attrs=dict(long_name="High-speed video data", units="Intensity"),
    )
    for coord in [time, utc, ypx, xpx]:
        images = coord.assign_to(images)
    return images, cine_header


def assign_length_scales(images: xr.DataArray) -> xr.DataArray:
    """Assign length scales to "x" and "y" coordinates."""
    parent_dim_units = "px"
    roi = load_roi(images.data, PARAMS.paths.examples / "roi_line.yaml", "line")
    pixels = euclidean(*iter(roi))
    um_per_px = SAMPLE_DIAMETER_UM / pixels
    y = get_length_scale(parent_dim_units, "y", "Height", um_per_px, images)
    x = get_length_scale(parent_dim_units, "x", "Width", um_per_px, images)
    images = y.assign_to(images)
    images = x.assign_to(images)
    return images


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
