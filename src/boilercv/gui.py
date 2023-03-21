"""Graphical user interface utilities."""

# ruff: noqa: N815

from collections.abc import Iterator, Sequence
from contextlib import contextmanager
from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np
import pyqtgraph as pg
import yaml
from aiohttp_retry import Any
from pycine.file import read_header
from pycine.raw import read_frames
from PySide6.QtCore import QEvent, Qt, Signal
from PySide6.QtGui import QKeyEvent
from PySide6.QtWidgets import QGridLayout, QHBoxLayout, QPushButton

from boilercv.images import load_roi
from boilercv.types import ArrDatetime, ArrGen, ArrIntDef, Img, ImgSeq, NBit_T


def compare_images(results: Sequence[Img[NBit_T] | ImgSeq[NBit_T]]):
    """Compare multiple sets of images or sets of timeseries of images."""
    results = [np.array(result) for result in results]
    num_results = len(results)
    with image_viewer(num_results) as (
        _app,
        _window,
        _layout,
        _button_layout,
        image_views,
    ):
        for result, image_view in zip(results, image_views, strict=False):
            image_view.setImage(result)


def preview_images(result: Img[NBit_T] | ImgSeq[NBit_T]):
    """Preview a single image or timeseries of images."""
    result = np.array(result)
    with image_viewer() as (_app, _window, _layout, _button_layout, image_views):
        image_views[0].setImage(result)


def get_video_images(
    cine_file: Path,
    start_frame: int | None = None,
    start_frame_cine: int | None = None,
    count: int | None = None,
) -> Iterator[Img[NBit_T]]:
    """Get images from a CINE video file."""
    images, *_ = read_frames(cine_file, start_frame, start_frame_cine, count)
    bpp = read_header(cine_file)["setup"].RealBPP
    return (image.astype(f"uint{bpp}") for image in images)


# * -------------------------------------------------------------------------------- * #


@dataclass
class Time64:
    """Time64 struct."""

    fractions: int
    seconds: int


@dataclass
class CineFileHeader:
    """CINE file header."""

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
    """Bitmap info header."""

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
class WBGain2:
    """White balance, gain correction."""

    R: float
    B: float


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
class Setup:
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


@dataclass
class Header:
    cinefileheader: CineFileHeader
    bitmapinfoheader: BitmapInfoHeader
    setup: Setup
    pImage: list[int]
    timestamp: ArrDatetime
    exposuretime: ArrGen


def get_header(cine_file: Path) -> Header:
    """Parse a CINE header."""

    header = read_header(cine_file)
    header = Header(**header)

    header.pImage = list(header.pImage)

    header.timestamp = header.timestamp.astype("datetime64[ns]")

    header.cinefileheader = CineFileHeader(**struct_to_dict(header.cinefileheader))
    header.cinefileheader.TriggerTime = Time64(
        **struct_to_dict(header.cinefileheader.TriggerTime)
    )

    header.bitmapinfoheader = BitmapInfoHeader(
        **struct_to_dict(header.bitmapinfoheader)
    )

    header.setup = handle_setup_values(header.setup)

    return header


def get_attrs_and_timestamps_from_header(
    header: Header,
) -> tuple[dict[str, Any], ArrDatetime]:
    """Flatten the header metadata into top-level attributes, extract timestamps."""

    cinefileheader = asdict(header.cinefileheader)

    # Exposure times are the same each frame, so just take the first one
    exposure_time = {"exposuretime": header.exposuretime[0]}

    trigger_time = asdict(header.cinefileheader.TriggerTime)
    del cinefileheader["TriggerTime"]

    bitmapinfoheader = asdict(header.bitmapinfoheader)
    setup = asdict(header.setup)

    autoexprect = asdict(header.setup.AutoExpRect)
    del setup["AutoExpRect"]

    wbview = asdict(header.setup.WBView)
    del setup["WBView"]

    uf = asdict(header.setup.UF)
    del setup["UF"]

    croprect = asdict(header.setup.CropRect)
    del setup["CropRect"]

    trigtc = asdict(header.setup.TrigTC)
    del setup["TrigTC"]

    wbgain = {
        f"WBGain{i}{color}": asdict(wb)[color]
        for i, wb in enumerate(header.setup.WBGain)
        for color in asdict(wb)
    }
    del setup["WBGain"]

    # These fields don't decode properly
    del setup["CreatedBy"]
    del setup["CameraModel"]

    return (
        (
            cinefileheader
            | exposure_time
            | trigger_time
            | bitmapinfoheader
            | setup
            | autoexprect
            | wbview
            | uf
            | croprect
            | trigtc
            | wbgain
        ),
        header.timestamp,
    )


def struct_to_dict(structure):
    """Convert a C-style structure to a dictionary from its `_fields_`."""
    return {
        field[0]: getattr(structure, field[0])
        for field in structure._fields_  # noqa: SLF001
    }


def handle_setup_values(setup: Setup):
    """Coerce setup values to Python objects."""

    setup = Setup(**struct_to_dict(setup))
    setup.WBGain = [WBGain2(**struct_to_dict(i)) for i in setup.WBGain]
    setup.WBView = WBGain2(**struct_to_dict(setup.WBView))
    setup.UF = ImFilter(**struct_to_dict(setup.UF))
    setup.CropRect = Rect(**struct_to_dict(setup.CropRect))
    setup.AutoExpRect = Rect(**struct_to_dict(setup.AutoExpRect))
    setup.TrigTC = TC(**struct_to_dict(setup.TrigTC))

    bytes_fields = [
        "DescriptionOld",
        "Description",
        "LensDescription",
        "ToneLabel",
        "UserMatrixLabel",
        "CineName",
        "CalibrationInfo",
        "OpticalFilter",
        "GpsInfo",
        "Uuid",
    ]
    for field in bytes_fields:
        setup.__dict__[field] = setup.__dict__[field].decode("ascii").rstrip("\x00")

    # These fields are invalid for the CINE file associated with Phantom v4.3
    _undecodable_fields = [
        "CreatedBy",
        "CameraModel",
    ]

    char_array_fields = ["BinName", "AnaUnit", "AnaName", "szCinePath"]
    for field in char_array_fields:
        setup.__dict__[field] = (
            np.char.decode(setup.__dict__[field], encoding="ascii")
            .tobytes()
            .decode("ascii")
            .rstrip("\x00")
        )

    list_fields = [
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
    ]
    for field in list_fields:
        setup.__dict__[field] = list(setup.__dict__[field])

    setup.UF.Coef = list(setup.UF.Coef)

    return setup


# * -------------------------------------------------------------------------------- * #


def edit_roi(roi_path: Path, image: Img[NBit_T]) -> ArrIntDef:
    """Edit the region of interest for an image."""

    with image_viewer() as (_app, window, _layout, button_layout, image_views):
        roi = pg.PolyLineROI(
            pen=pg.mkPen("red"),
            hoverPen=pg.mkPen("magenta"),
            handlePen=pg.mkPen("blue"),
            handleHoverPen=pg.mkPen("magenta"),
            closed=True,
            positions=load_roi(roi_path, image),
        )

        def main():
            """Allow ROI interaction."""
            window.key_signal.connect(keyPressEvent)
            button = QPushButton("Save ROI")
            button.clicked.connect(save_roi)  # type: ignore
            button_layout.addWidget(button)
            image_views[0].setImage(image)
            image_views[0].addItem(roi)

        def keyPressEvent(ev: QKeyEvent):  # noqa: N802
            """Save ROI or quit on key presses."""
            if ev.key() == Qt.Key.Key_S:
                save_roi()
                ev.accept()

        def save_roi():
            """Save the ROI."""
            vertices = get_roi_vertices()
            roi_path.write_text(
                encoding="utf-8", data=yaml.safe_dump(vertices.tolist(), indent=2)
            )

        def get_roi_vertices() -> ArrIntDef:
            """Get the vertices of the ROI."""
            return np.array(roi.saveState()["points"], dtype=int)

        main()

    return get_roi_vertices()


@contextmanager
def image_viewer(num_views: int = 1):  # noqa: C901
    """View and interact with images and video."""
    # Isolate pg.ImageView in a layout cell. It is complicated to directly modify the UI
    # of pg.ImageView. Can't use the convenient pg.LayoutWidget because
    # GraphicsLayoutWidget cannot contain it, and GraphicsLayoutWidget is convenient on
    # its own.
    image_view_grid_size = int(np.ceil(np.sqrt(num_views)))
    app = pg.mkQApp()
    image_views: list[pg.ImageView] = []
    layout = QGridLayout()
    button_layout = QHBoxLayout()
    window = GraphicsLayoutWidgetWithKeySignal(show=True, size=(800, 600))
    window.setLayout(layout)

    def main():
        add_image_views()
        add_actions()
        try:
            yield app, window, layout, button_layout, image_views
        finally:
            app.exec()

    def add_image_views():
        if num_views == 2:  # noqa: PLR2004
            coordinates = [(0, 0), (0, 1)]
        else:
            coordinates = get_square_grid_coordinates(image_view_grid_size)
        for column in range(image_view_grid_size):
            layout.setColumnStretch(column, 1)
        for coordinate in coordinates:
            image_view = get_image_view()
            layout.addWidget(image_view, *coordinate)
            image_views.append(image_view)

    def add_actions():
        window.key_signal.connect(keyPressEvent)
        layout.addLayout(
            button_layout, image_view_grid_size, 0, 1, image_view_grid_size
        )
        if num_views > 1:
            add_button(button_layout, "Toggle Play All", trigger_space).setFocus()
        add_button(button_layout, "Continue", app.quit)

    def keyPressEvent(ev: QKeyEvent):  # noqa: N802
        """Handle quit events and propagate keypresses to image views."""
        if ev.key() in (Qt.Key.Key_Escape, Qt.Key.Key_Q, Qt.Key.Key_Enter):
            app.quit()
            ev.accept()
        for image_view in image_views:
            image_view.keyPressEvent(ev)

    def trigger_space():
        keyPressEvent(
            QKeyEvent(
                QEvent.Type.KeyPress, Qt.Key.Key_Space, Qt.KeyboardModifier.NoModifier
            )
        )

    yield from main()


class GraphicsLayoutWidgetWithKeySignal(pg.GraphicsLayoutWidget):
    """Emit key signals on `key_signal`."""

    key_signal = Signal(QKeyEvent)

    def keyPressEvent(self, ev: QKeyEvent):  # noqa: N802
        super().keyPressEvent(ev)
        self.key_signal.emit(ev)


def add_button(layout, label, callback):
    button = QPushButton(label)
    button.clicked.connect(callback)  # type: ignore
    layout.addWidget(button)
    return button


def get_image_view() -> pg.ImageView:
    """Get an image view suitable for previewing images."""
    image_view = pg.ImageView()
    image_view.playRate = 30
    image_view.ui.histogram.hide()
    image_view.ui.roiBtn.hide()
    image_view.ui.menuBtn.hide()
    return image_view


def get_square_grid_coordinates(n: int) -> Iterator[ArrIntDef]:
    """Get the coordinates of a square grid."""
    x, y = np.indices((n, n))
    yield from np.column_stack((x.ravel(), y.ravel()))
