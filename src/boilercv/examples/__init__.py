"""Examples, experiments, and demonstrations."""

from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

import cv2 as cv
import pyqtgraph as pg
from pycine.file import read_header
from pycine.raw import read_frames
from pyqtgraph.Qt import QtCore

from boilercv.examples.contours import GraphicsLayoutWidgetWithKeySignal
from boilercv.types import Img, NBit_T


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


def video_images(path: Path) -> Iterator[Img[NBit_T]]:
    """Images from a video file."""
    bpp = read_header(path)["setup"].RealBPP
    images, *_ = read_frames(cine_file=path)
    return (image.astype(f"uint{bpp}") for image in images)


@contextmanager
def video_capture_images(path: Path):
    """Images from a video file."""
    video_capture = cv.VideoCapture(str(path))
    try:
        yield get_video_capture_image(video_capture)
    finally:
        video_capture.release()


def get_video_capture_image(video_capture: cv.VideoCapture) -> Iterator[Img[NBit_T]]:
    """Get an image from a video capture."""
    while True:
        read_is_successful, image = video_capture.read()
        if not read_is_successful:
            break
        yield image


@contextmanager
def qt_window():
    """Create a Qt window with a given name and size."""
    app = pg.mkQApp()
    try:
        yield app, GraphicsLayoutWidgetWithKeySignal(show=True, size=(800, 600))
    finally:
        app.exec()


def has_channels(image: Img[NBit_T], channels: int):
    """Check whether an image has a given number of channels."""
    number_of_channels = image.shape[-1]
    return number_of_channels == channels


def gray_to_rgb(image: Img[NBit_T]) -> Img[NBit_T]:
    return convert_image(image, cv.COLOR_GRAY2RGB)


def rgb_to_gray(image: Img[NBit_T]) -> Img[NBit_T]:
    return convert_image(image, cv.COLOR_RGB2GRAY)


def bgr_to_rgb(image: Img[NBit_T]) -> Img[NBit_T]:
    return convert_image(image, cv.COLOR_BGR2RGB)


def get_first_channel(image: Img[NBit_T]) -> Img[NBit_T]:
    """Return just the first channel of an image."""
    return image[:, :, 0]


def convert_image(image: Img[NBit_T], code: int | None = None) -> Img[NBit_T]:
    """Convert image format, handling inconsistent type annotations."""
    return image if code is None else cv.cvtColor(image, code)
