"""Computer vision routines suitable for nucleate pool boiling bubble analysis."""

from collections.abc import Iterable, Iterator
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
from PySide6.QtWidgets import QGridLayout

from boilercv.models.params import Params
from boilercv.types import Img, Img8, NBit, NBit_T

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


def get_video_images(cine_file: Path) -> Iterator[Img[NBit]]:
    """Get images from a CINE video file."""
    images, *_ = read_frames(cine_file=cine_file)
    bpp = read_header(cine_file)["setup"].RealBPP
    return (image.astype(f"uint{bpp}") for image in images)


def preview_images(result: list[Img[NBit_T]] | Img[NBit_T]):
    with qt_window() as (_app, _window, _layout, image_view):
        image_view.setImage(np.array(result))


def convert_image(image: Img[NBit_T], code: int | None = None) -> Img[NBit_T]:
    """Convert image format, handling inconsistent type annotations."""
    return image if code is None else cv.cvtColor(image, code)  # type: ignore


def get_8bit_images(images: Iterable[Img[NBit]]) -> Iterator[Img8]:
    """Assume images are 8-bit."""
    return (_8_bit(image) for image in images)


def _8_bit(image: Img[NBit]) -> Img8:
    """Assume an image is 8-bit."""
    return image  # type: ignore


class GraphicsLayoutWidgetWithKeySignal(pg.GraphicsLayoutWidget):
    """Emit key signals on `key_signal`."""

    key_signal = Signal(QKeyEvent)

    def keyPressEvent(self, event: QKeyEvent):  # noqa: N802
        super().keyPressEvent(event)
        self.key_signal.emit(event)


@contextmanager
def qt_window():
    """Create a Qt window with a given name and size."""
    app = pg.mkQApp()
    try:
        # Isolate pg.ImageView in a layout cell. It is complicated to directly modify
        # the UI of pg.ImageView. Can't use the convenient pg.LayoutWidget because
        # GraphicsLayoutWidget cannot contain it, and GraphicsLayoutWidget is convenient
        # on its own.

        image_view = pg.ImageView()
        image_view.playRate = 30
        image_view.ui.histogram.hide()
        image_view.ui.roiBtn.hide()
        image_view.ui.menuBtn.hide()

        layout = QGridLayout()
        layout.addWidget(image_view)

        window = GraphicsLayoutWidgetWithKeySignal(show=True, size=(800, 600))
        window.setLayout(layout)

        yield app, window, layout, image_view
    finally:
        app.exec()
