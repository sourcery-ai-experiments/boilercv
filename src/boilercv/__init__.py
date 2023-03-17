"""Computer vision routines suitable for nucleate pool boiling bubble analysis."""
from collections.abc import Iterable, Iterator, Sequence
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
from PySide6.QtCore import QEvent, Qt, Signal
from PySide6.QtGui import QKeyEvent
from PySide6.QtWidgets import QGridLayout, QPushButton

from boilercv.models.params import Params
from boilercv.types import ArrIntDef, Img, Img8, ImgSeq, NBit, NBit_T

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


def convert_image(image: Img[NBit_T], code: int | None = None) -> Img[NBit_T]:
    """Convert image format, handling inconsistent type annotations."""
    return image if code is None else cv.cvtColor(image, code)  # type: ignore


def get_8bit_images(images: Iterable[Img[NBit]]) -> Iterator[Img8]:
    """Assume images are 8-bit."""
    return (_8_bit(image) for image in images)


def _8_bit(image: Img[NBit]) -> Img8:
    """Assume an image is 8-bit."""
    return image  # type: ignore


# * -------------------------------------------------------------------------------- * #


def get_video_images(cine_file: Path) -> Iterator[Img[NBit_T]]:
    """Get images from a CINE video file."""
    images, *_ = read_frames(cine_file=cine_file)
    bpp = read_header(cine_file)["setup"].RealBPP
    return (image.astype(f"uint{bpp}") for image in images)


def compare_images(results: Sequence[Img[NBit_T] | ImgSeq[NBit_T]]):
    """Compare multiple sets of images or sets of timeseries of images."""
    results = [np.array(result) for result in results]
    num_results = len(results)
    with qt_window(num_results) as (_app, _window, _layout, image_views):
        for result, image_view in zip(results, image_views, strict=False):
            image_view.setImage(result)


def preview_images(result: Img[NBit_T] | ImgSeq[NBit_T]):
    """Preview a single image or timeseries of images."""
    result = np.array(result)
    with qt_window() as (_app, _window, _layout, image_views):
        image_views[0].setImage(result)


@contextmanager
def qt_window(num_views: int = 1):  # noqa: C901
    """Create a Qt window with a given name and size."""
    # Isolate pg.ImageView in a layout cell. It is complicated to directly modify the UI
    # of pg.ImageView. Can't use the convenient pg.LayoutWidget because
    # GraphicsLayoutWidget cannot contain it, and GraphicsLayoutWidget is convenient on
    # its own.
    app = pg.mkQApp()
    image_views: list[pg.ImageView] = []
    layout = QGridLayout()
    window = GraphicsLayoutWidgetWithKeySignal(show=True, size=(800, 600))
    grid_size = int(np.ceil(np.sqrt(num_views)))

    def main():
        window.setLayout(layout)
        window.key_signal.connect(keyPressEvent)
        if num_views == 2:  # noqa: PLR2004
            coordinates = [(0, 0), (0, 1)]
        else:
            coordinates = get_square_grid_coordinates(grid_size)
        for column in range(grid_size):
            layout.setColumnStretch(column, 1)
        for coordinate in coordinates:
            image_view = get_image_view()
            layout.addWidget(image_view, *coordinate)
            image_views.append(image_view)
        try:
            yield app, window, layout, image_views
        finally:
            add_buttons()
            app.exec()

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

    def add_buttons():
        button_row = grid_size + 1
        if num_views > 1:
            add_button(
                layout, "Toggle Play All", trigger_space, button_row, grid_size
            ).setDefault(True)
            button_row += 1
        add_button(layout, "Continue", app.quit, button_row, grid_size).setDefault(
            False
        )

    yield from main()


class GraphicsLayoutWidgetWithKeySignal(pg.GraphicsLayoutWidget):
    """Emit key signals on `key_signal`."""

    key_signal = Signal(QKeyEvent)

    def keyPressEvent(self, ev: QKeyEvent):  # noqa: N802
        super().keyPressEvent(ev)
        self.key_signal.emit(ev)


def add_button(layout, label, callback, row, width):
    button = QPushButton(label)
    button.clicked.connect(callback)  # type: ignore
    layout.addWidget(button, row, 0, 1, width)
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
