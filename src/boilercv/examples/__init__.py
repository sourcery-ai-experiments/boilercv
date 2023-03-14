"""Examples, experiments, and demonstrations."""

from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

import cv2 as cv
import pyqtgraph as pg
from loguru import logger
from pyqtgraph.Qt import QtCore

from boilercv.types import Img, NBit_T

pg.setConfigOption("imageAxisOrder", "row-major")


def play_video(data):
    """Play a video."""
    app = pg.mkQApp()

    window = pg.GraphicsLayoutWidget()
    window.show()

    view = window.addViewBox(invertY=True)
    view.setAspectLocked(True)
    view.invertY = True

    image_item = pg.ImageItem(axisOrder="row-major")

    view.addItem(image_item)

    frame = 0
    elapsed = 0
    timer = QtCore.QTimer()  # type: ignore
    timer.setSingleShot(True)

    def update_data():
        nonlocal image_item, data, frame, elapsed
        image_item.setImage(data[frame])
        frame = (frame + 1) % data.shape[0]
        timer.start()

    timer.timeout.connect(update_data)
    update_data()
    app.exec()


def interact_with_video(data: Img[NBit_T]):
    """Interact with video."""
    app = pg.mkQApp()
    image_view = pg.ImageView()
    image_view.ui.histogram.hide()
    image_view.ui.roiBtn.hide()
    image_view.ui.menuBtn.hide()
    image_view.setImage(data)
    (_, width, height) = data.shape
    roi = pg.CircleROI([0.5, 0.5], min(width, height))
    image_view.addItem(roi)

    def roi_changed():
        nonlocal roi
        logger.trace(roi.saveState())

    roi.sigRegionChanged.connect(roi_changed)
    image_view.show()
    app.exec()


# connecting roi changed signal to custom function


@contextmanager
def video_images(path: Path):
    """Images from a video file."""
    cap = cv.VideoCapture(str(path))
    try:
        yield get_image(cap)
    finally:
        cap.release()


def get_image(video_capture: cv.VideoCapture) -> Iterator[Img[NBit_T]]:
    """Get an image from a video capture."""
    while True:
        read_is_successful, image = video_capture.read()
        if not read_is_successful:
            break
        yield image


def has_channels(image: Img[NBit_T], channels: int):
    """Check whether an image has a given number of channels."""
    number_of_channels = image.shape[-1]
    return number_of_channels == channels


def rgb_to_gray(image: Img[NBit_T]) -> Img[NBit_T]:
    return convert_image(image, cv.COLOR_RGB2GRAY)


def bgr_to_rgb(image: Img[NBit_T]) -> Img[NBit_T]:
    return convert_image(image, cv.COLOR_BGR2RGB)


def convert_image(image: Img[NBit_T], code: int | None = None) -> Img[NBit_T]:
    """Convert image format, handling inconsistent type annotations."""
    return image if code is None else cv.cvtColor(image, code)  # type: ignore
