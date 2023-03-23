"""Models and operations specific to CINE files."""

from collections.abc import Iterator
from dataclasses import asdict, dataclass
from datetime import tzinfo
from pathlib import Path

import numpy as np
import xarray as xr
from pycine.raw import read_frames
from scipy.spatial.distance import euclidean

from boilercv import SAMPLE_DIAMETER_UM, TIMEZONE
from boilercv.images import load_roi
from boilercv.models.params import PARAMS
from boilercv.types import ArrDatetime, ArrIntDef, Img, NBit_T
from boilercv.video.cine.models import FlatHeader, FlatHeaderStudySpecific, Header

MIN_VER = 691
"""The version of Phantom Camera Control or Cine Viewer software to read monochrome.

Files produced by earlier versions do not encode black level and white level into the
header file, which is used by pycine to scale the raw data. For videos produced by older
software, reproduce the video using a newer version of Phantom Cine Viewer so the
correct header information is embedded.

See: https://github.com/ottomatic-io/pycine/blob/815cfca06cafc50745a43b2cd0168982225c6dca/pycine/raw.py#L176
"""


@dataclass
class UnitScale:
    """A unit scale."""

    dim: str
    units: str
    scale: float


def load_cine(
    cine_source: Path,
    num_frames: int | None = None,
    start_frame: int = 0,
) -> xr.DataArray:
    """Load images from a CINE to an xr.DataArray."""

    variable_name = "images"
    length_units = "um"
    length_scale = SAMPLE_DIAMETER_UM
    y = UnitScale("y", length_units, length_scale)
    x = UnitScale("x", length_units, length_scale)
    ns_to_s = 1e-9
    time = UnitScale("time", "s", ns_to_s)

    header, utc = get_cine_attributes(cine_source, TIMEZONE, num_frames, start_frame)

    if header.SoftwareVersion < MIN_VER:
        raise RuntimeError(
            f"CINE file produced by software older than {MIN_VER}. Reproduce the video"
            " in a newer version of Phantom Cine Viewer and try again."
        )

    elapsed = (utc - utc[0]).astype(float) / time.scale
    images = xr.DataArray(
        name=variable_name,
        dims=(time.dim, y.dim, x.dim),
        coords=dict(time=elapsed, utc=(time.dim, utc)),
        data=list(get_cine_images(cine_source, num_frames, start_frame)),
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

    return images


def get_cine_images(
    cine_file: Path,
    num_frames: int | None = None,
    start_frame: int = 0,
) -> Iterator[Img[NBit_T]]:
    """Get images from a CINE video file."""
    images, _, bpp = read_frames(cine_file, start_frame=start_frame, count=num_frames)  # type: ignore
    return (image.astype(f"uint{bpp}") for image in images)


def get_cine_attributes(
    cine_file: Path,
    timezone: tzinfo,
    num_frames: int | None = None,
    start_frame: int = 0,
) -> tuple[FlatHeaderStudySpecific, ArrDatetime]:
    """Flatten the header metadata into top-level attributes, extract timestamps.

    Specific to the Phantom v4.3 high-speed camera and Phantom Camera Control software
    version used in this study. Exposure time is constant, so it becomes part of the
    metadata.
    """
    header = Header.from_file(cine_file, timezone)
    flat = FlatHeader.from_header(header, timezone)
    flat_specific = FlatHeaderStudySpecific.from_flat_header(
        flat, header.exposuretime[start_frame]
    )
    utc = (
        header.utc[start_frame : start_frame + num_frames] if num_frames else header.utc
    )
    return flat_specific, utc
