"""Models and operations specific to CINE files."""

from datetime import tzinfo
from pathlib import Path

from boilercv.types import ArrDatetime
from boilercv.video.cine.models import (
    FlatHeaderStudySpecific,
    Header,
    flatten_header,
    remove_study_specific_fields,
)


def get_cine_attributes(
    cine_file: Path, timezone: tzinfo
) -> tuple[FlatHeaderStudySpecific, ArrDatetime]:
    """Flatten the header metadata into top-level attributes, extract timestamps.

    Specific to the Phantom v4.3 high-speed camera and Phantom Camera Control software
    version used in this study. Exposure time is constant, so it becomes part of the
    metadata.
    """

    header = Header.from_file(cine_file, timezone)
    flat, utc, exposuretime = flatten_header(header, timezone)
    flat = remove_study_specific_fields(flat, exposuretime[0])
    return (flat, utc)
