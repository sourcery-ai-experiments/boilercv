"""Models and operations specific to CINE files."""

from copy import copy
from datetime import tzinfo
from pathlib import Path
from typing import Any

from boilercv.types import ArrDatetime
from boilercv.video.cine.models import Header, flatten_header


def get_cine_attributes(
    cine_file: Path, timezone: tzinfo
) -> tuple[dict[str, Any], ArrDatetime]:
    """Flatten the header metadata into top-level attributes, extract timestamps.

    Specific to the Phantom v4.3 high-speed camera and Phantom Camera Control software
    version used in this study. Exposure time is constant, so it becomes part of the
    metadata.
    """

    header = Header.from_file(cine_file, timezone)
    (flat, utc, exposuretime) = flatten_header(header, timezone)
    flat = remove_study_specific_fields(flat)
    flat["ExposureTime"] = exposuretime[0]
    return (flat, utc)


CINE_HEADER_INVALID_FIELDS_THIS_STUDY = {"OffImageHeader", "OffSetup"}
"""These fields are invalid for the camera and PCC software used in this study."""

SETUP_INVALID_FIELDS_THIS_STUDY = {
    "TrigTC",
    "fPbRate",
    "fTcRate",
    "CineName",
    "fGainR",
    "fGainG",
    "fGainB",
    "cmCalib",
    "fWBTemp",
    "fWBCc",
    "CalibrationInfo",
    "OpticalFilter",
    "GpsInfo",
    "Uuid",
    "CreatedBy",
    "RecBPP",
    "LowestFormatBPP",
    "LowestFormatQ",
    "fToe",
    "LogMode",
    "CameraModel",
    "WBType",
    "fDecimation",
    "MagSerial",
    "CSSerial",
    "dFrameRate",
    "SensorMode",
}
"""These setup fields are invalid for the camera and PCC software used in this study."""


def remove_study_specific_fields(flat: dict[str, Any]) -> dict[str, Any]:
    """Remove fields specific to this study."""
    flat_specific = copy(flat)
    for field in flat:
        if any(
            field.startswith(invalid_field)
            for invalid_field in CINE_HEADER_INVALID_FIELDS_THIS_STUDY
        ):
            del flat_specific[field]
        if any(
            field.startswith(invalid_field)
            for invalid_field in SETUP_INVALID_FIELDS_THIS_STUDY
        ):
            del flat_specific[field]
    return flat_specific
