"""Models and operations specific to CINE files."""

from dataclasses import asdict, dataclass
from datetime import tzinfo
from pathlib import Path

import numpy as np
import xarray as xr
from scipy.spatial.distance import euclidean

from boilercv import SAMPLE_DIAMETER_UM, TIMEZONE, get_8bit_images
from boilercv.gui import get_video_images
from boilercv.images import load_roi
from boilercv.models.params import PARAMS
from boilercv.types import ArrDatetime, ArrIntDef
from boilercv.video.cine.models import FlatHeader, FlatHeaderStudySpecific, Header


@dataclass
class UnitScale:
    """A unit scale."""

    dim: str
    units: str
    scale: float


def convert_cine_to_netcdf(variable_name: str, cine_source: Path, nc_destination: Path):
    """Convert CINE to NetCDF."""

    length_units = "um"
    length_scale = SAMPLE_DIAMETER_UM
    y = UnitScale("y", length_units, length_scale)
    x = UnitScale("x", length_units, length_scale)
    ns_to_s = 1e-9
    time = UnitScale("time", "s", ns_to_s)

    header, utc = get_cine_attributes(cine_source, TIMEZONE)
    elapsed = (utc - utc[0]).astype(float) / time.scale
    images = xr.DataArray(
        name=variable_name,
        dims=(time.dim, y.dim, x.dim),
        coords=dict(time=elapsed, utc=(time.dim, utc)),
        data=list(get_8bit_images(get_video_images(cine_source))),
        attrs=asdict(header)
        | dict(long_name="High-speed video data", units="intensity"),
    )
    images["time"] = images.time.assign_attrs(
        dict(long_name="Time elapsed", units=time.units)
    )
    images["utc"] = images.utc.assign_attrs(dict(long_name="UTC time"))

    roi = load_roi(images.data, PARAMS.paths.examples / "roi_line.yaml", "line")
    px_per_um = euclidean(*iter(roi)) / x.scale

    def scale(coord: ArrIntDef) -> ArrIntDef:
        """Scale coordinates to nanometers."""
        return np.round(coord / px_per_um).astype(int)

    images = images.assign_coords(dict(y=scale(images.y), x=scale(images.x)))

    images["y"] = images.y.assign_attrs(dict(long_name="Height", units=length_scale))
    images["x"] = images.x.assign_attrs(dict(long_name="Width", units=length_scale))

    xr.Dataset(coords={variable_name: images}).to_netcdf(path=nc_destination)


def get_cine_attributes(
    cine_file: Path, timezone: tzinfo
) -> tuple[FlatHeaderStudySpecific, ArrDatetime]:
    """Flatten the header metadata into top-level attributes, extract timestamps.

    Specific to the Phantom v4.3 high-speed camera and Phantom Camera Control software
    version used in this study. Exposure time is constant, so it becomes part of the
    metadata.
    """
    header = Header.from_file(cine_file, timezone)
    flat = FlatHeader.from_header(header, timezone)
    return (
        FlatHeaderStudySpecific.from_flat_header(flat, header.exposuretime[0]),
        header.utc,
    )
