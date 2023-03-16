"""Computer vision routines suitable for nucleate pool boiling bubble analysis."""

from collections.abc import Iterator
from contextlib import contextmanager
from os import environ
from pathlib import Path
from textwrap import dedent

import cv2 as cv
import numpy as np
import pyqtgraph as pg
from cv2 import version
from pycine.file import read_header
from pycine.raw import read_frames
from PySide6.QtCore import Signal
from PySide6.QtGui import QKeyEvent

from boilercv.models.params import Params
from boilercv.types import ArrIntDef, Img, Img8, NBit, NBit_T

__version__ = "0.0.0"


NO_CONTRIB_MSG = dedent(
    """\
    OpenCV is not installed with extras. A dependent package may have pinned
    `opencv-pyhon` and clobbered your installed version.
    """
)
WHITE = (255, 255, 255)
MARKER_COLOR = (0, 0, 255)
PARAMS = Params.get_params()


def init():
    """Initialize the package."""
    check_contrib()
    check_samples_env_var()
    pg.setConfigOption("imageAxisOrder", "row-major")


def check_contrib():
    """Ensure the installed version of OpenCV has extras.

    Dependencies can specify a different version of OpenCV than the one required in this
    project, unintentionally clobbering the installed version of OpenCV. Detect whether
    a non-`contrib` version is installed by a dependency.
    """
    if not version.contrib:
        raise ImportError(NO_CONTRIB_MSG)


def check_samples_env_var():
    """Check that the OpenCV samples environment variable is set and is a folder."""
    samples_env_var = "OPENCV_SAMPLES_DATA_PATH"
    if (
        not (samples_dir := environ.get(samples_env_var))
        or not Path(samples_dir).is_dir()
    ):
        raise RuntimeError(
            f"{samples_env_var} not set or specified directory does not exist."
        )


init()

# * -------------------------------------------------------------------------------- * #


def video_images_8bit(path: Path) -> Iterator[Img8]:
    """Images from a CINE video file with 8-bit depth."""
    bpp = read_header(path)["setup"].RealBPP
    return (_8_bit(image.astype(f"uint{bpp}")) for image in video_images(path))


def video_images(path: Path) -> Iterator[Img[NBit]]:
    """Images from a CINE video file."""
    images, *_ = read_frames(cine_file=path)
    return images


@contextmanager
def qt_window():
    """Create a Qt window with a given name and size."""
    app = pg.mkQApp()
    try:
        yield app, GraphicsLayoutWidgetWithKeySignal(show=True, size=(800, 600))
    finally:
        app.exec()


class GraphicsLayoutWidgetWithKeySignal(pg.GraphicsLayoutWidget):
    """Emit key signals on `key_signal`."""

    key_signal = Signal(QKeyEvent)

    def keyPressEvent(self, event: QKeyEvent):  # noqa: N802
        self.scene().keyPressEvent(event)
        self.key_signal.emit(event)
        super().keyPressEvent(event)


def mask_and_threshold(image: Img[NBit_T], roi: ArrIntDef) -> Img[NBit_T]:
    """Mask an image and threshold it."""
    blank = np.zeros_like(image)
    mask: Img[NBit_T] = ~cv.fillConvexPoly(blank, roi, WHITE)
    masked = cv.add(image, mask)
    return cv.adaptiveThreshold(
        src=masked,
        maxValue=np.iinfo(masked.dtype).max,
        adaptiveMethod=cv.ADAPTIVE_THRESH_MEAN_C,
        thresholdType=cv.THRESH_BINARY,
        blockSize=11,
        C=2,
    )


def convert_image(image: Img[NBit_T], code: int | None = None) -> Img[NBit_T]:
    """Convert image format, handling inconsistent type annotations."""
    return image if code is None else cv.cvtColor(image, code)  # type: ignore


def _8_bit(image: Img[NBit]) -> Img8:
    """Assume an image is 8-bit."""
    return image  # type: ignore
