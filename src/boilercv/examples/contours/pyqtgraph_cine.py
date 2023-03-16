"""Given a CINE, find ROI using `pyqtgraph` and find contours."""


import numpy as np
import pyqtgraph as pg
import yaml
from pycine.raw import read_frames
from PySide6.QtCore import Qt
from PySide6.QtGui import QKeyEvent
from PySide6.QtWidgets import QGridLayout

from boilercv import PARAMS
from boilercv.examples.contours import mask_and_threshold, qt_window
from boilercv.models.params import Params
from boilercv.types import ArrIntDef, Img, Img8, NBit_T


def main():
    images, *_ = read_frames(
        cine_file=Params.get_params().paths.examples_data
        / "results_2022-11-30T12-39-07_98C.cine"
    )
    image: Img8 = next(images)
    roi = get_roi(image)
    mask_and_threshold(image, roi)


def get_roi(data: Img[NBit_T]) -> ArrIntDef:
    """Get the region of interest of an image."""

    # Load or initialize the ROI
    app = pg.mkQApp()
    (width, height) = data.shape[-2:]
    saved_roi = PARAMS.paths.examples_data / "roi.yaml"
    if saved_roi.exists():
        positions = yaml.safe_load(saved_roi.read_text(encoding="utf-8"))
    else:
        positions = [(0, 0), (0, width), (height, width), (height, 0)]
    roi = pg.PolyLineROI(
        pen=pg.mkPen("red"),
        hoverPen=pg.mkPen("magenta"),
        handlePen=pg.mkPen("blue"),
        handleHoverPen=pg.mkPen("magenta"),
        closed=True,
        positions=positions,
    )

    def main():
        """Lay out the widget and connect callbacks."""
        with qt_window() as window:
            window.key_signal.connect(handle_keys)

            layout = QGridLayout()
            window.setLayout(layout)

            image_view = pg.ImageView()
            image_view.playRate = 30
            image_view.ui.histogram.hide()
            image_view.ui.roiBtn.hide()
            image_view.ui.menuBtn.hide()
            image_view.setImage(data)
            layout.addWidget(image_view, 0, 0)

            image_view.addItem(roi)

            button = pg.QtWidgets.QPushButton("Save ROI")
            button.clicked.connect(save_roi)
            layout.addWidget(button, 1, 0)

        return save_roi()

    def handle_keys(event: QKeyEvent):
        """Save ROI or quit on key presses."""
        if any(event.key() == key for key in (Qt.Key.Key_Escape, Qt.Key.Key_Q)):
            app.quit()
        if event.key() == Qt.Key.Key_S:
            save_roi()

    def save_roi() -> ArrIntDef:
        """Save the ROI."""
        nonlocal roi
        vertices = roi.saveState()["points"]
        saved_roi.write_text(
            encoding="utf-8",
            data=yaml.safe_dump(vertices, indent=2),
        )
        return np.array(vertices, dtype=int)

    return main()


if __name__ == "__main__":
    main()
