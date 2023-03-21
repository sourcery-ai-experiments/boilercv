"""Models and operations specific to CINE files."""

from copy import copy
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from pycine.file import read_header

from boilercv.types import ArrDatetime, ArrFloat64
from boilercv.video.cine.models import (
    BitmapInfoHeader,
    CineFileHeader,
    Setup,
    Time64,
    flatten_header,
    struct_to_dict,
)


@dataclass
class Header:
    """Top-level header for CINE file metadata.

    See: https://github.com/ottomatic-io/pycine/blob/815cfca06cafc50745a43b2cd0168982225c6dca/pycine/file.py#L15
    """

    cinefileheader: CineFileHeader
    bitmapinfoheader: BitmapInfoHeader
    setup: Setup

    pImage: list[int]
    """List of pointers to each image in the video for low-level indexing."""

    timestamp: ArrDatetime
    """Array of timestamps for each image in the video."""

    exposuretime: ArrFloat64
    """Array of exposure times for each image in the video."""

    def __post_init__(self):
        """Convert low-level structures to dataclasses."""
        self.cinefileheader = CineFileHeader(**struct_to_dict(self.cinefileheader))
        self.cinefileheader.TriggerTime = Time64(
            **struct_to_dict(self.cinefileheader.TriggerTime)
        )
        self.bitmapinfoheader = BitmapInfoHeader(
            **struct_to_dict(self.bitmapinfoheader)
        )
        self.setup = Setup(**struct_to_dict(self.setup))
        self.pImage = list(self.pImage)
        self.timestamp = self.timestamp.astype("datetime64[ns]")
        return self

    @classmethod
    def from_file(cls, cine_file: Path):
        """Extract the header from a CINE file."""
        return cls(**read_header(cine_file))


def flatten_header_study_specific(
    header: Header,
) -> tuple[dict[str, Any], ArrDatetime]:
    """Flatten the header metadata into top-level attributes, extract timestamps.

    Specific to the Phantom v4.3 high-speed camera and Phantom Camera Control software
    version used in this study. Exposure time is constant, so it becomes part of the
    metadata.
    """

    (flat, timestamp, exposuretime) = flatten_header(header)
    flat = remove_study_specific_fields(flat)
    flat["ExposureTime"] = exposuretime[0]
    return (flat, timestamp)


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
