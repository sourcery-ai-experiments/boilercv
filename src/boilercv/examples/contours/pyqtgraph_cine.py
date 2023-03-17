"""Given a CINE, find ROI using `pyqtgraph` and find contours."""
from pathlib import Path

import numpy as np
import pyqtgraph as pg
import yaml
from PySide6.QtCore import Qt
from PySide6.QtGui import QKeyEvent
from PySide6.QtWidgets import QPushButton

from boilercv import (
    PARAMS,
    compare_images,
    get_8bit_images,
    get_video_images,
    preview_images,
    qt_window,
)
from boilercv.examples.contours import draw_contours, find_contours, mask, threshold
from boilercv.types import ArrIntDef, Img, ImgSeq8, NBit_T


def main():
    images = get_8bit_images(
        get_video_images(
            PARAMS.paths.examples_data / "results_2022-11-30T12-39-07_98C.cine"
        )
    )
    roi = edit_roi(PARAMS.paths.examples_data / "roi.yaml", next(images))
    result: ImgSeq8 = []
    for image in images:
        masked = mask(image, roi)
        thresholded = threshold(masked)
        contours, _ = find_contours(thresholded)
        result.append(draw_contours(image, contours))
    preview_images(result)
    compare_images([result, result])
    compare_images([result, result, result])


def edit_roi(roi_path: Path, image: Img[NBit_T]) -> ArrIntDef:
    """Edit the region of interest for an image."""

    with qt_window() as (_app, window, layout, image_views):
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
            layout.addWidget(button)
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
                encoding="utf-8",
                data=yaml.safe_dump(vertices.tolist(), indent=2),
            )

        def get_roi_vertices() -> ArrIntDef:
            """Get the vertices of the ROI."""
            return np.array(roi.saveState()["points"], dtype=int)

        main()

    return get_roi_vertices()


def load_roi(roi_path: Path, image: Img[NBit_T]) -> ArrIntDef:
    """Load the region of interest for an image."""
    (width, height) = image.shape[-2:]
    if roi_path.exists():
        vertices: list[tuple[int, int]] = yaml.safe_load(
            roi_path.read_text(encoding="utf-8")
        )
    else:
        vertices = [(0, 0), (0, width), (height, width), (height, 0)]
    return np.array(vertices, dtype=int)


if __name__ == "__main__":
    main()
