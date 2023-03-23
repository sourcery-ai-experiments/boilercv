"""Models and operations specific to CINE files."""

from collections.abc import Iterator
from datetime import tzinfo
from pathlib import Path

from pycine.raw import read_frames

from boilercv.types import ArrDatetime, Img, NBit_T
from boilercv.video.cine.models import FlatHeader, FlatHeaderStudySpecific, Header

MIN_VER = 691
"""The version of Phantom Camera Control or Cine Viewer software to read monochrome.

Files produced by earlier versions do not encode black level and white level into the
header file, which is used by pycine to scale the raw data. For videos produced by older
software, reproduce the video using a newer version of Phantom Cine Viewer so the
correct header information is embedded.

See: https://github.com/ottomatic-io/pycine/blob/815cfca06cafc50745a43b2cd0168982225c6dca/pycine/raw.py#L176
"""


def get_cine_images(
    cine_file: Path,
    num_frames: int | None = None,
    start_frame: int = 0,
) -> Iterator[Img[NBit_T]]:
    """Get images from a CINE video file."""
    images, setup, bpp = read_frames(cine_file, start_frame=start_frame, count=num_frames)  # type: ignore
    if setup.SoftwareVersion < MIN_VER:
        raise RuntimeError(
            f"CINE file produced by software older than {MIN_VER}. Reproduce the video"
            " in a newer version of Phantom Cine Viewer and try again."
        )
    yield from (image.astype(f"uint{bpp}") for image in images)


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
