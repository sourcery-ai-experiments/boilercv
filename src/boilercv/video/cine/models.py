"""Models for CINE file metadata."""

from contextlib import suppress
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from typing import Any

import numpy as np

from boilercv.types import ArrDatetime, ArrFloat64
from boilercv.video.cine import Header


def struct_to_dict(structure):
    """Convert a C-style structure to a dictionary from its `_fields_`."""
    return {
        field[0]: getattr(structure, field[0])
        for field in structure._fields_  # noqa: SLF001
    }


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

        bytes_type_fields = {
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
        for field in bytes_type_fields:
            # Version-specific invalid fields will point to invalid memory addresses
            with suppress(UnicodeDecodeError):
                self.__dict__[field] = (
                    self.__dict__[field].decode("ascii").rstrip("\x00")
                )

        char_array_fields = ["BinName", "AnaUnit", "AnaName", "szCinePath"]
        for field in char_array_fields:
            self.__dict__[field] = (
                np.char.decode(self.__dict__[field], encoding="ascii")
                .tobytes()
                .decode("ascii")
                .rstrip("\x00")
            )

        list_type_fields = {
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
        for field in list_type_fields:
            self.__dict__[field] = list(self.__dict__[field])


SETUP_IGNORED_FIELDS = {
    "Res7",
    "Res8",
    "Res9",
    "Res10",
    "Res11",
    "Res12",
    "Res13",
    "Res6",
    "Res14",
    "Res15",
    "Res16",
    "Res17",
    "Res18",
    "Res19",
    "Res20",
    "Res1",
    "Res2",
    "Res3",
    "Res5",
    "Res21",
    "Conv8Min",
    "Res4",
}
"""Ignore these fields.

See: https://github.com/ottomatic-io/pycine/blob/815cfca06cafc50745a43b2cd0168982225c6dca/pycine/cine.py#L185
"""

FIELDS_MAPPING_UPDATED_TO_ORIGINAL = {
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


def remove_outdated_fields_from_setup(setup_full: Setup) -> dict[str, Any]:
    """Ensure updated fields are valid and delete outdated and ignored fields."""
    setup: dict[str, Any] = asdict(setup_full)
    for updated, original in FIELDS_MAPPING_UPDATED_TO_ORIGINAL.items():
        if not setup.get(original):
            continue
        if (
            setup[updated] == setup[original]
            or ("16" in updated and 1000 * setup[updated] == setup[original])
            or (updated in ["Saturation", "Contrast", "Gamma", "Conv8Max"])
        ):
            del setup[original]
        else:
            raise RuntimeError("Could not map updated field to original.")
    for field in SETUP_IGNORED_FIELDS:
        del setup[field]
    return setup


def flatten_header(
    header: Header,
) -> tuple[dict[str, Any], ArrDatetime, ArrFloat64]:
    """Flatten the header metadata into top-level attributes and extract timestamps."""
    flat: dict[str, Any] = {}
    cinefileheader = asdict(header.cinefileheader)
    for field, value in cinefileheader.items():
        if field == "TriggerTime":
            trigger_time = cinefileheader[field]
            flat[field] = (
                datetime.fromtimestamp(trigger_time["seconds"])
                + timedelta(seconds=trigger_time["fractions"] / 2**32)
            ).isoformat()
        else:
            flat[field] = value
    for field, value in asdict(header.bitmapinfoheader).items():
        flat[field] = value
    setup = remove_outdated_fields_from_setup(header.setup)
    for field, value in setup.items():
        if field in {"AutoExpRect", "WBView", "CropRect", "TrigTC", "UF"}:
            flat |= {
                f"{field}{subfield}": subvalue
                for subfield, subvalue in setup[field].items()
            }
        elif field == "WBGain":
            flat |= {
                f"{field}{i}{color}": wb[color]
                for i, wb in enumerate(setup["WBGain"])
                for color in wb
            }
        else:
            flat[field] = value
    return (flat, header.timestamp, header.exposuretime)
