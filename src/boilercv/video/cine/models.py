"""Models for CINE file metadata."""

from contextlib import suppress
from dataclasses import InitVar, asdict, dataclass
from datetime import UTC, datetime, timedelta, tzinfo
from pathlib import Path
from typing import Any, Self

import numpy as np
from pycine.file import read_header

from boilercv import npa
from boilercv.types import ArrDT, ArrFloat

BYTES_TYPE_FIELDS = {
    "CalibrationInfo",
    "CameraModel",
    "CineName",
    "CreatedBy",
    "Description",
    "DescriptionOld",
    "GpsInfo",
    "LensDescription",
    "OpticalFilter",
    "ToneLabel",
    "UserMatrixLabel",
    "Uuid",
}

CHAR_ARRAY_FIELDS = {"BinName", "AnaUnit", "AnaName", "szCinePath"}

LIST_TYPE_FIELDS = {
    "ChOption",
    "AnaGain",
    "FRPImgNr",
    "FRPRate",
    "FRPExp",
    "MCPercent",
    "HeadSerial",
    "Res4",
    "fTone",
    "cmUser",
    "FRPShape",
    "cmCalib",
}

SETUP_IGNORED_FIELDS = {
    "Conv8Min",
    "Res1",
    "Res10",
    "Res11",
    "Res12",
    "Res13",
    "Res14",
    "Res15",
    "Res16",
    "Res17",
    "Res18",
    "Res19",
    "Res2",
    "Res20",
    "Res21",
    "Res3",
    "Res4",
    "Res5",
    "Res6",
    "Res7",
    "Res8",
    "Res9",
}
"""Ignore these fields.

See: https://github.com/ottomatic-io/pycine/blob/815cfca06cafc50745a43b2cd0168982225c6dca/pycine/cine.py#L185
"""

SETUP_FIELDS_MAPPING_ORIGINAL_TO_UPDATED = {
    "AspectRatio": "ImWidth, ImHeight",
    "FrameRate16": "FrameRate",
    "Shutter16": "ShutterNs",
    "PostTrigger16": "PostTrigger",
    "FrameDelay16": "FrameDelayNs",
    "DescriptionOld": "Description",
    "EDRShutter16": "EDRShutterNs",
    "Saturation": "fSaturation",
    "Shutter": "ShutterNs",
    "EDRShutter": "EDRShutterNs",
    "FrameDelay": "FrameDelayNs",
    "Bright": "fOffset",
    "Contrast": "fGain",
    "Gamma": "fGamma",
    "Conv8Max": "fGain16_8",
    "Hue": "fHue",
}
"""Use the updated fields here instead of the original ones.

See: https://github.com/ottomatic-io/pycine/blob/815cfca06cafc50745a43b2cd0168982225c6dca/pycine/cine.py#L174
"""

SETUP_FIELDS_TO_REMOVE = (
    set(SETUP_FIELDS_MAPPING_ORIGINAL_TO_UPDATED) | SETUP_IGNORED_FIELDS
)

CINE_HEADER_INVALID_FIELDS_THIS_STUDY = {"OffImageHeader", "OffSetup"}
"""These fields are invalid for the camera and PCC software used in this study."""

SETUP_INVALID_FIELDS_THIS_STUDY = {
    # Using passive lenses
    "LensDescription",
    "LensAperture",
    "LensFocusDistance",
    "LensFocalLength",
    # Setup file ends here in this study
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

FIELDS_TO_REMOVE_THIS_STUDY = (
    BYTES_TYPE_FIELDS
    | CHAR_ARRAY_FIELDS
    | CINE_HEADER_INVALID_FIELDS_THIS_STUDY
    | SETUP_INVALID_FIELDS_THIS_STUDY
)


def struct_to_dict(structure):
    """Convert a C-style structure to a dictionary from its `_fields_`."""
    return {
        field[0]: getattr(structure, field[0])
        for field in structure._fields_  # noqa: SLF001
    }


def capfirst(string: str) -> str:
    """Capitalize the first letter of a string."""
    return f"{string[0].upper()}{string[1:]}"


@dataclass
class Time64:
    """Time64 struct.

    See: https://github.com/ottomatic-io/pycine/blob/815cfca06cafc50745a43b2cd0168982225c6dca/pycine/cine.py#L50
    """

    fractions: int
    seconds: int


@dataclass
class ImFilter:
    """Image filter."""

    dim: int
    shifts: int
    bias: int
    Coef: list[int]


@dataclass
class Rect:
    """Crop rectangle."""

    left: int
    top: int
    right: int
    bottom: int


@dataclass
class TC:
    """Time code according to the standard SMPTE 12M-1999."""

    framesU: int
    framesT: int
    dropFrameFlag: int
    colorFrameFlag: int
    secondsU: int
    secondsT: int
    flag1: int
    minutesU: int
    minutesT: int
    flag2: int
    hoursU: int
    hoursT: int
    flag3: int
    flag4: int
    userBitData: int


@dataclass
class WBGain2:
    """White balance, gain correction."""

    R: float
    B: float


@dataclass
class CineFileHeader:
    """CINE file header.

    See: https://github.com/ottomatic-io/pycine/blob/815cfca06cafc50745a43b2cd0168982225c6dca/pycine/cine.py#L539
    """

    Type: int
    Headersize: int
    Compression: int
    Version: int
    FirstMovieImage: int
    TotalImageCount: int
    FirstImageNo: int
    ImageCount: int
    OffImageHeader: int
    OffSetup: int
    OffImageOffsets: int
    TriggerTime: Time64


@dataclass
class BitmapInfoHeader:
    """Bitmap info header.

    See: https://github.com/ottomatic-io/pycine/blob/815cfca06cafc50745a43b2cd0168982225c6dca/pycine/cine.py#L560
    """

    biSize: int
    biWidth: int
    biHeight: int
    biPlanes: int
    biBitCount: int
    biCompression: int
    biSizeImage: int
    biXPelsPerMeter: int
    biYPelsPerMeter: int
    biClrUsed: int
    biClrImportant: int


@dataclass
class Setup:
    """Setup header.

    See: https://github.com/ottomatic-io/pycine/blob/815cfca06cafc50745a43b2cd0168982225c6dca/pycine/cine.py#L191
    """

    FrameRate16: int
    Shutter16: int
    PostTrigger16: int
    FrameDelay16: int
    AspectRatio: int
    Res7: int
    Res8: int
    Res9: int
    Res10: int
    Res11: int
    TrigFrame: int
    Res12: int
    DescriptionOld: bytes
    Mark: int
    Length: int
    Res13: int
    SigOption: int
    BinChannels: int
    SamplesPerImage: int
    BinName: bytes
    AnaOption: int
    AnaChannels: int
    Res6: int
    AnaBoard: int
    ChOption: list[int]
    AnaGain: list[float]
    AnaUnit: bytes
    AnaName: bytes
    lFirstImage: int
    dwImageCount: int
    nQFactor: int
    wCineFileType: int
    szCinePath: bytes
    Res14: int
    Res15: int
    Res16: int
    Res17: int
    Res18: float
    Res19: float
    Res20: int
    Res1: int
    Res2: int
    Res3: int
    ImWidth: int
    ImHeight: int
    EDRShutter16: int
    Serial: int
    Saturation: int
    Res5: int
    AutoExposure: int
    bFlipH: bool
    bFlipV: bool
    Grid: int
    FrameRate: int
    Shutter: int
    EDRShutter: int
    PostTrigger: int
    FrameDelay: int
    bEnableColor: bool
    CameraVersion: int
    FirmwareVersion: int
    SoftwareVersion: int
    RecordingTimeZone: int
    CFA: int
    Bright: int
    Contrast: int
    Gamma: int
    Res21: int
    AutoExpLevel: int
    AutoExpSpeed: int
    AutoExpRect: Rect
    WBGain: list[WBGain2]
    Rotate: int
    WBView: WBGain2
    RealBPP: int
    Conv8Min: int
    Conv8Max: int
    FilterCode: int
    FilterParam: int
    UF: ImFilter
    BlackCalSVer: int
    WhiteCalSVer: int
    GrayCalSVer: int
    bStampTime: bool
    SoundDest: int
    FRPSteps: int
    FRPImgNr: list[int]
    FRPRate: list[int]
    FRPExp: list[int]
    MCCnt: int
    MCPercent: list[float]
    CICalib: int
    CalibWidth: int
    CalibHeight: int
    CalibRate: int
    CalibExp: int
    CalibEDR: int
    CalibTemp: int
    HeadSerial: list[int]
    RangeCode: int
    RangeSize: int
    Decimation: int
    MasterSerial: int
    Sensor: int
    ShutterNs: int
    EDRShutterNs: int
    FrameDelayNs: int
    ImPosXAcq: int
    ImPosYAcq: int
    ImWidthAcq: int
    ImHeightAcq: int
    Description: bytes
    RisingEdge: bool
    FilterTime: int
    LongReady: bool
    ShutterOff: bool
    Res4: list[int]
    bMetaWB: bool
    Hue: int
    BlackLevel: int
    WhiteLevel: int
    LensDescription: bytes
    LensAperture: float
    LensFocusDistance: float
    LensFocalLength: float
    fOffset: float
    fGain: float
    fSaturation: float
    fHue: float
    fGamma: float
    fGammaR: float
    fGammaB: float
    fFlare: float
    fPedestalR: float
    fPedestalG: float
    fPedestalB: float
    fChroma: float
    ToneLabel: bytes
    TonePoints: int
    fTone: list[float]
    UserMatrixLabel: bytes
    EnableMatrices: bool
    cmUser: list[float]
    EnableCrop: bool
    CropRect: Rect
    EnableResample: bool
    ResampleWidth: int
    ResampleHeight: int
    fGain16_8: float
    FRPShape: list[int]
    TrigTC: TC
    fPbRate: float
    fTcRate: float
    CineName: bytes
    fGainR: float
    fGainG: float
    fGainB: float
    cmCalib: list[float]
    fWBTemp: float
    fWBCc: float
    CalibrationInfo: bytes
    OpticalFilter: bytes
    GpsInfo: bytes
    Uuid: bytes
    CreatedBy: bytes
    RecBPP: int
    LowestFormatBPP: int
    LowestFormatQ: int
    fToe: float
    LogMode: int
    CameraModel: bytes
    WBType: int
    fDecimation: float
    MagSerial: int
    CSSerial: int
    dFrameRate: float
    SensorMode: int

    def __post_init__(self):
        """Convert low-level structures to dataclasses."""

        self.WBGain = [WBGain2(**struct_to_dict(i)) for i in self.WBGain]
        self.WBView = WBGain2(**struct_to_dict(self.WBView))
        self.UF = ImFilter(**struct_to_dict(self.UF))  # type: ignore
        self.UF.Coef = list(self.UF.Coef)
        self.CropRect = Rect(**struct_to_dict(self.CropRect))
        self.AutoExpRect = Rect(**struct_to_dict(self.AutoExpRect))
        self.TrigTC = TC(**struct_to_dict(self.TrigTC))

        for field in BYTES_TYPE_FIELDS:
            # Version-specific invalid fields will point to invalid memory addresses
            with suppress(UnicodeDecodeError):
                self.__dict__[field] = (
                    self.__dict__[field].decode("ascii").rstrip("\x00")
                )

        for field in CHAR_ARRAY_FIELDS:
            self.__dict__[field] = (
                np.char.decode(self.__dict__[field], encoding="ascii")
                .tobytes()
                .decode("ascii")
                .rstrip("\x00")
            )

        for field in LIST_TYPE_FIELDS:
            self.__dict__[field] = list(self.__dict__[field])


@dataclass
class Header:
    """Top-level header for CINE file metadata.
    See: https://github.com/ottomatic-io/pycine/blob/815cfca06cafc50745a43b2cd0168982225c6dca/pycine/file.py#L15.
    """

    cinefileheader: CineFileHeader
    bitmapinfoheader: BitmapInfoHeader
    setup: Setup

    pImage: list[int]
    """List of pointers to each image in the video for low-level indexing."""

    timestamp: ArrFloat
    """Array of timestamps for each image in the video."""

    utc: ArrDT
    """Array of the UTC time for each image in the video."""

    exposuretime: ArrFloat
    """Array of exposure times for each image in the video."""

    timezone: InitVar[tzinfo]
    """The timezone in which the video was created."""

    def __post_init__(self, timezone: tzinfo):
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
        self.utc = npa(
            [
                datetime.fromtimestamp(timestamp, timezone)
                .astimezone(UTC)
                .replace(tzinfo=None)
                for timestamp in self.timestamp
            ],
            dtype="datetime64[ns]",
        )
        return self

    @classmethod
    def from_file(cls, cine_file: Path, timezone: tzinfo) -> Self:
        """Extract the header from a CINE file."""
        return cls(
            **read_header(cine_file),
            timezone=timezone,
            utc=None,  # type: ignore  # Handled in __post_init__
        )


@dataclass
class FlatHeader:
    """Flattened header for CINE file metadata."""

    Type: int
    Headersize: int
    Compression: int
    Version: int
    FirstMovieImage: int
    TotalImageCount: int
    FirstImageNo: int
    ImageCount: int
    OffImageHeader: int
    OffSetup: int
    OffImageOffsets: int
    TriggerTime: str
    BiSize: int
    BiWidth: int
    BiHeight: int
    BiPlanes: int
    BiBitCount: int
    BiCompression: int
    BiSizeImage: int
    BiXPelsPerMeter: int
    BiYPelsPerMeter: int
    BiClrUsed: int
    BiClrImportant: int
    TrigFrame: int
    Mark: int
    Length: int
    SigOption: int
    BinChannels: int
    SamplesPerImage: int
    BinName: bytes
    AnaOption: int
    AnaChannels: int
    AnaBoard: int
    ChOption: list[int]
    AnaGain: list[float]
    AnaUnit: bytes
    AnaName: bytes
    LFirstImage: int
    DwImageCount: int
    NQFactor: int
    WCineFileType: int
    SzCinePath: bytes
    ImWidth: int
    ImHeight: int
    Serial: int
    AutoExposure: int
    BFlipH: bool
    BFlipV: bool
    FrameRate: int
    Grid: int
    PostTrigger: int
    BEnableColor: bool
    CameraVersion: int
    FirmwareVersion: int
    SoftwareVersion: int
    RecordingTimeZone: int
    CFA: int
    AutoExpLevel: int
    AutoExpSpeed: int
    AutoExpRectLeft: int
    AutoExpRectTop: int
    AutoExpRectRight: int
    AutoExpRectBottom: int
    WBGain0R: float
    WBGain0B: float
    WBGain1R: float
    WBGain1B: float
    WBGain2R: float
    WBGain2B: float
    WBGain3R: float
    WBGain3B: float
    Rotate: int
    WBViewR: float
    WBViewB: float
    RealBPP: int
    FilterCode: int
    FilterParam: int
    UFDim: int
    UFShifts: int
    UFBias: int
    UFCoef: list[int]
    BlackCalSVer: int
    WhiteCalSVer: int
    GrayCalSVer: int
    BStampTime: bool
    SoundDest: int
    FRPSteps: int
    FRPImgNr: list[int]
    FRPRate: list[int]
    FRPExp: list[int]
    MCCnt: int
    MCPercent: list[float]
    CICalib: int
    CalibWidth: int
    CalibHeight: int
    CalibRate: int
    CalibExp: int
    CalibEDR: int
    CalibTemp: int
    HeadSerial: list[int]
    RangeCode: int
    RangeSize: int
    Decimation: int
    MasterSerial: int
    Sensor: int
    ShutterNs: int
    EDRShutterNs: int
    FrameDelayNs: int
    ImPosXAcq: int
    ImPosYAcq: int
    ImWidthAcq: int
    ImHeightAcq: int
    Description: bytes
    RisingEdge: bool
    FilterTime: int
    LongReady: bool
    ShutterOff: bool
    BMetaWB: bool
    BlackLevel: int
    WhiteLevel: int
    LensDescription: bytes
    LensAperture: float
    LensFocusDistance: float
    LensFocalLength: float
    FOffset: float
    FGain: float
    FSaturation: float
    FHue: float
    FGamma: float
    FGammaR: float
    FGammaB: float
    FFlare: float
    FPedestalR: float
    FPedestalG: float
    FPedestalB: float
    FChroma: float
    ToneLabel: bytes
    TonePoints: int
    FTone: list[float]
    UserMatrixLabel: bytes
    EnableMatrices: bool
    CmUser: list[float]
    EnableCrop: bool
    CropRectLeft: int
    CropRectTop: int
    CropRectRight: int
    CropRectBottom: int
    EnableResample: bool
    ResampleWidth: int
    ResampleHeight: int
    FGain16_8: float
    FRPShape: list[int]
    TrigTCFramesU: int
    TrigTCFramesT: int
    TrigTCDropFrameFlag: int
    TrigTCColorFrameFlag: int
    TrigTCSecondsU: int
    TrigTCSecondsT: int
    TrigTCFlag1: int
    TrigTCMinutesU: int
    TrigTCMinutesT: int
    TrigTCFlag2: int
    TrigTCHoursU: int
    TrigTCHoursT: int
    TrigTCFlag3: int
    TrigTCFlag4: int
    TrigTCUserBitData: int
    FPbRate: float
    FTcRate: float
    CineName: bytes
    FGainR: float
    FGainG: float
    FGainB: float
    CmCalib: list[float]
    FWBTemp: float
    FWBCc: float
    CalibrationInfo: bytes
    OpticalFilter: bytes
    GpsInfo: bytes
    Uuid: bytes
    CreatedBy: bytes
    RecBPP: int
    LowestFormatBPP: int
    LowestFormatQ: int
    FToe: float
    LogMode: int
    CameraModel: bytes
    WBType: int
    FDecimation: float
    MagSerial: int
    CSSerial: int
    DFrameRate: float
    SensorMode: int

    @classmethod
    def from_header(cls, header: Header, timezone: tzinfo) -> Self:
        """Flatten a header."""
        flat: dict[str, Any] = {}
        cinefileheader = asdict(header.cinefileheader)
        for field, value in cinefileheader.items():
            if field == "TriggerTime":
                trigger_time = cinefileheader[field]
                flat[capfirst(field)] = (
                    datetime.fromtimestamp(
                        trigger_time["seconds"],
                        timezone,
                    ).astimezone(UTC)
                    + timedelta(seconds=trigger_time["fractions"] / 2**32)
                ).isoformat()
            else:
                flat[capfirst(field)] = value
        for field, value in asdict(header.bitmapinfoheader).items():
            flat[capfirst(field)] = value
        setup = {
            field: value
            for field, value in asdict(header.setup).items()
            if field not in SETUP_FIELDS_TO_REMOVE
        }
        for field, value in setup.items():
            if field in {"AutoExpRect", "WBView", "CropRect", "TrigTC", "UF"}:
                flat |= {
                    f"{field}{capfirst(subfield)}": subvalue
                    for subfield, subvalue in setup[field].items()
                }
            elif field == "WBGain":
                flat |= {
                    f"{capfirst(field)}{i}{capfirst(color)}": wb[color]
                    for i, wb in enumerate(setup["WBGain"])
                    for color in wb
                }
            else:
                flat[capfirst(field)] = value
        return cls(**flat)


@dataclass
class FlatHeaderStudySpecific:
    ExposureTime: int
    Type: int
    Headersize: int
    Compression: int
    Version: int
    FirstMovieImage: int
    TotalImageCount: int
    FirstImageNo: int
    ImageCount: int
    OffImageOffsets: int
    TriggerTime: str
    BiSize: int
    BiWidth: int
    BiHeight: int
    BiPlanes: int
    BiBitCount: int
    BiCompression: int
    BiSizeImage: int
    BiXPelsPerMeter: int
    BiYPelsPerMeter: int
    BiClrUsed: int
    BiClrImportant: int
    TrigFrame: int
    Mark: int
    Length: int
    SigOption: int
    BinChannels: int
    SamplesPerImage: int
    AnaOption: int
    AnaChannels: int
    AnaBoard: int
    ChOption: list[int]
    AnaGain: list[float]
    LFirstImage: int
    DwImageCount: int
    NQFactor: int
    WCineFileType: int
    ImWidth: int
    ImHeight: int
    Serial: int
    AutoExposure: int
    BFlipH: bool
    BFlipV: bool
    FrameRate: int
    Grid: int
    PostTrigger: int
    BEnableColor: bool
    CameraVersion: int
    FirmwareVersion: int
    SoftwareVersion: int
    RecordingTimeZone: int
    CFA: int
    AutoExpLevel: int
    AutoExpSpeed: int
    AutoExpRectLeft: int
    AutoExpRectTop: int
    AutoExpRectRight: int
    AutoExpRectBottom: int
    WBGain0R: float
    WBGain0B: float
    WBGain1R: float
    WBGain1B: float
    WBGain2R: float
    WBGain2B: float
    WBGain3R: float
    WBGain3B: float
    Rotate: int
    WBViewR: float
    WBViewB: float
    RealBPP: int
    FilterCode: int
    FilterParam: int
    UFDim: int
    UFShifts: int
    UFBias: int
    UFCoef: list[int]
    BlackCalSVer: int
    WhiteCalSVer: int
    GrayCalSVer: int
    BStampTime: bool
    SoundDest: int
    FRPSteps: int
    FRPImgNr: list[int]
    FRPRate: list[int]
    FRPExp: list[int]
    MCCnt: int
    MCPercent: list[float]
    CICalib: int
    CalibWidth: int
    CalibHeight: int
    CalibRate: int
    CalibExp: int
    CalibEDR: int
    CalibTemp: int
    HeadSerial: list[int]
    RangeCode: int
    RangeSize: int
    Decimation: int
    MasterSerial: int
    Sensor: int
    ShutterNs: int
    EDRShutterNs: int
    FrameDelayNs: int
    ImPosXAcq: int
    ImPosYAcq: int
    ImWidthAcq: int
    ImHeightAcq: int
    RisingEdge: bool
    FilterTime: int
    LongReady: bool
    ShutterOff: bool
    BMetaWB: bool
    BlackLevel: int
    WhiteLevel: int
    FOffset: float
    FGain: float
    FSaturation: float
    FHue: float
    FGamma: float
    FGammaR: float
    FGammaB: float
    FFlare: float
    FPedestalR: float
    FPedestalG: float
    FPedestalB: float
    FChroma: float
    TonePoints: int
    FTone: list[float]
    EnableMatrices: bool
    CmUser: list[float]
    EnableCrop: bool
    CropRectLeft: int
    CropRectTop: int
    CropRectRight: int
    CropRectBottom: int
    EnableResample: bool
    ResampleWidth: int
    ResampleHeight: int
    FGain16_8: float
    FRPShape: list[int]

    @classmethod
    def from_flat_header(cls, flat: FlatHeader, exposure_time: int) -> Self:
        """Remove fields specific to this study."""
        flat_dict = asdict(flat)
        flat_specific_dict: dict[str, Any] = {"ExposureTime": exposure_time}
        for field in flat_dict:
            if all(
                capfirst(field_part) not in field
                for field_part in FIELDS_TO_REMOVE_THIS_STUDY
            ):
                flat_specific_dict[field] = flat_dict[field]
        return cls(**flat_specific_dict)
