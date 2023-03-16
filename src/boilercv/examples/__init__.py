"""Examples, experiments, and demonstrations."""


import cv2 as cv
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore

from boilercv import convert_image
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
    timer = QtCore.QTimer()
    timer.setSingleShot(True)

    def update_data():
        nonlocal image_item, data, frame, elapsed
        image_item.setImage(data[frame])
        frame = (frame + 1) % data.shape[0]
        timer.start()

    timer.timeout.connect(update_data)
    update_data()
    app.exec()


def rgb_to_gray(image: Img[NBit_T]) -> Img[NBit_T]:
    return convert_image(image, cv.COLOR_RGB2GRAY)


def bgr_to_rgb(image: Img[NBit_T]) -> Img[NBit_T]:
    return convert_image(image, cv.COLOR_BGR2RGB)


def get_first_channel(image: Img[NBit_T]) -> Img[NBit_T]:
    """Return just the first channel of an image."""
    return image[:, :, 0]
