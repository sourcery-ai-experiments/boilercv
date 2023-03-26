"""Dataset model."""


from dataclasses import asdict
from pathlib import Path

import xarray as xr
from pytz import timezone
from scipy.spatial.distance import euclidean

from boilercv.data import assign_ds
from boilercv.data.models import Dimension
from boilercv.gui import load_roi
from boilercv.models.params import PARAMS
from boilercv.types import DA, DS, ArrInt
from boilercv.video.cine import get_cine_attributes, get_cine_images

TIMEZONE = timezone("US/Pacific")
VIDEO = "video"
HEADER = "header"
PRIMARY_LENGTH_UNITS = "px"
POINT_COORDS = ["ypx", "xpx"]
LINE_COORDS = ["ypx1", "xpx1", "ypx2", "xpx2"]
ROI = "roi"
OTHER_ROI = "roi_other"
SECONDARY_LENGTH_UNITS = "um"
SAMPLE_DIAMETER_UM = 9_525_000


def prepare_dataset(
    cine_source: Path, num_frames: int | None = None, start_frame: int = 0
) -> DS:
    """Prepare a dataset from a CINE."""

    # Header
    header, utc_arr = get_cine_attributes(
        cine_source, TIMEZONE, num_frames, start_frame
    )
    header_da = xr.DataArray(name=HEADER, attrs=asdict(header))

    # Dimensions
    frames = Dimension(
        dim="frame",
        long_name="Frame number",
    )
    ypx = Dimension(
        dim="ypx",
        long_name="Height",
        units="px",
    )
    xpx = Dimension(
        dim="xpx",
        long_name="Width",
        units="px",
    )
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

    # Dataset
    ds = assign_ds(
        name=VIDEO,
        long_name="High-speed video data",
        units="Pixel intensity",
        dims=(frames, ypx, xpx),
        secondary_dims=(time, utc),
        data=list(get_cine_images(cine_source, num_frames, start_frame)),
    )
    ds[header_da.name] = header_da
    return ds


# * -------------------------------------------------------------------------------- * #
# * ROI


def assign_roi_ds(ds: DS, roi_contour: ArrInt) -> DS:
    """Pack a contour into a DataArray."""
    return assign_ds(
        ds=ds,
        name=ROI,
        long_name="Region of interest",
        units=PRIMARY_LENGTH_UNITS,
        dims=(
            Dimension(
                dim="roi_vertex",
                long_name="ROI vertex",
            ),
            Dimension(
                dim="roi_loc",
                long_name="ROI vertex location",
                coords=POINT_COORDS,
            ),
        ),
        data=roi_contour,
    )


def assign_other_roi_ds(ds: DS, contours: list[ArrInt]) -> DS:
    """Pack a contour into a DataArray."""
    return assign_ds(
        ds=ds,
        name=OTHER_ROI,
        long_name="Excess detected regions of interest",
        units=PRIMARY_LENGTH_UNITS,
        dims=(
            Dimension(
                dim="contour",
                long_name="Extra contour",
            ),
            Dimension(
                dim="contour_vertex",
                long_name="Extra contour vertex",
            ),
            Dimension(
                dim="contour_loc",
                long_name="Contour vertex location",
                coords=POINT_COORDS,
            ),
        ),
        data=contours,
    )


# * -------------------------------------------------------------------------------- * #
# * SECONDARY LENGTH DIMENSIONS


def assign_length_dims(dataset: DS) -> DS:
    """Assign length scales to "x" and "y" coordinates."""
    images = dataset[VIDEO]
    parent_dim_units = "px"
    roi = load_roi(images.data, PARAMS.paths.examples / "roi_line.yaml", "line")
    pixels = euclidean(*iter(roi))
    um_per_px = SAMPLE_DIAMETER_UM / pixels
    y = get_length_dims(parent_dim_units, "y", "Height", um_per_px, images)
    x = get_length_dims(parent_dim_units, "x", "Width", um_per_px, images)
    images = y.assign_to(images)
    images = x.assign_to(images)
    return dataset


def get_length_dims(
    parent_dim_units: str, dim: str, long_name: str, scale: float, images: DA
) -> Dimension:
    """Get a length scale."""
    parent_dim = f"{dim}{parent_dim_units}"
    return Dimension(
        parent_dim=f"{dim}{parent_dim_units}",
        dim=dim,
        long_name=long_name,
        units=SECONDARY_LENGTH_UNITS,
        original_units=parent_dim_units,
        original_coords=images[parent_dim].values,
        scale=scale,
    )
