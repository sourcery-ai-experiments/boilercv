from contextlib import contextmanager

import cv2 as cv
import numpy as np
import pyqtgraph as pg
from PySide6.QtCore import Signal
from PySide6.QtGui import QKeyEvent

from boilercv import WHITE
from boilercv.types import ArrIntDef, Img, NBit_T

ESC_KEY = ord("\x1b")


@contextmanager
def qt_window():
    """Create a Qt window with a given name and size."""
    app = pg.mkQApp()
    yield GraphicsLayoutWidgetWithKeySignal(show=True, size=(800, 600))
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
