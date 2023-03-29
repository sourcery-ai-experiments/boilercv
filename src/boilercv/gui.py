"""Graphical user interface utilities."""

import inspect
from collections.abc import Iterator, Mapping, Sequence
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal, TypeAlias

import numpy as np
import pyqtgraph as pg
import yaml
from PySide6.QtCore import QEvent, Qt, Signal
from PySide6.QtGui import QKeyEvent
from PySide6.QtWidgets import QGridLayout, QHBoxLayout, QPushButton

from boilercv.images import scale_bool
from boilercv.types import ArrInt, Img

Viewable: TypeAlias = Any  # The true type is a complex union of lots of array types
NamedViewable: TypeAlias = Mapping[str | int, Viewable]
MultipleViewable: TypeAlias = Sequence[Viewable]
AllViewable: TypeAlias = Viewable | NamedViewable | MultipleViewable


def view_images(images: AllViewable, name: str = ""):
    """Compare multiple images or videos."""
    with image_viewer(images, name):
        pass


# * -------------------------------------------------------------------------------- * #


def save_roi(roi_vertices: ArrInt, roi_path: Path):
    """Save an ROI represented by an ordered array of vertices."""
    roi_path.write_text(
        encoding="utf-8", data=yaml.safe_dump(roi_vertices.tolist(), indent=2)
    )


def edit_roi(
    image: ArrInt, roi_path: Path, roi_type: Literal["poly", "line"] = "poly"
) -> ArrInt:
    """Edit the region of interest for an image."""

    with image_viewer(image) as (image_views, _app, window, _layout, button_layout):
        common_roi_args = dict(
            pen=pg.mkPen("red"),
            hoverPen=pg.mkPen("magenta"),
            handlePen=pg.mkPen("blue"),
            handleHoverPen=pg.mkPen("magenta"),
            positions=load_roi(image, roi_path, roi_type),
        )
        roi = (
            pg.PolyLineROI(
                **common_roi_args,
                closed=True,
            )
            if roi_type == "poly"
            else pg.LineSegmentROI(**common_roi_args)
        )

        def main():
            """Allow ROI interaction."""
            window.key_signal.connect(keyPressEvent)
            button = QPushButton("Save ROI")
            button.clicked.connect(save_roi_)  # type: ignore
            button_layout.addWidget(button)
            image_views["_0"].setImage(image)
            image_views["_0"].addItem(roi)

        def keyPressEvent(ev: QKeyEvent):  # noqa: N802
            """Save ROI or quit on key presses."""
            if ev.key() == Qt.Key.Key_S:
                save_roi_()
                ev.accept()

        def save_roi_():
            """Save the ROI."""
            vertices = get_roi_vertices()
            save_roi(vertices, roi_path)

        def get_roi_vertices() -> ArrInt:
            """Get the vertices of the ROI."""
            return np.array(roi.saveState()["points"], dtype=int)

        main()

    return get_roi_vertices()


def load_roi(
    img: Img,
    roi_path: Path,
    roi_type: Literal["poly", "line"] = "poly",
) -> ArrInt:
    """Load the region of interest for an image."""
    (width, height) = img.shape[-2:]
    if roi_path.exists():
        vertices: list[tuple[int, int]] = yaml.safe_load(
            roi_path.read_text(encoding="utf-8")
        )
    else:
        vertices = (
            [(0, 0), (0, width), (height, width), (height, 0)]
            if roi_type == "poly"
            else [(0, 0), (height, width)]
        )
    return np.array(vertices, dtype=int)


# * -------------------------------------------------------------------------------- * #

WINDOW_SIZE = (800, 600)
WINDOW_NAME = "Image viewer"


@dataclass
class Grid:
    """A grid of certain shape with coordinates to its cells."""

    shape: tuple[int, int]
    """The shape of the grid specified by (rows, columns)."""

    @property
    def coords(self) -> list[tuple[int, int]]:
        """The coordinates of the grid."""
        (y, x) = np.ones(self.shape).nonzero()
        return list(zip(y, x, strict=True))


GRIDS = {
    num_views: Grid(shape)
    for num_views, shape in {
        1: (1, 1),
        2: (1, 2),
        3: (1, 3),
        4: (2, 4),
        5: (2, 3),
        6: (2, 3),
        7: (2, 4),
        8: (2, 4),
        9: (2, 5),
        10: (2, 5),
        11: (3, 4),
        12: (3, 4),
    }.items()
}


@contextmanager
def image_viewer(images: AllViewable, name: str = ""):  # noqa: C901  # type: ignore
    """View and interact with images and video."""
    # Isolate pg.ImageView in a layout cell. It is complicated to directly modify the UI
    # of pg.ImageView. Can't use the convenient pg.LayoutWidget because
    # GraphicsLayoutWidget cannot contain it, and GraphicsLayoutWidget is convenient on
    # its own.
    images: NamedViewable = coerce_images(images)
    num_views = len(images)
    if num_views > len(GRIDS):
        square_length = int(np.ceil(np.sqrt(num_views)))
        (height, width) = (square_length, square_length)
    else:
        (height, width) = GRIDS[num_views].shape
    app = pg.mkQApp()
    image_views: list[pg.ImageView] = []
    layout = QGridLayout()
    button_layout = QHBoxLayout()
    window = GraphicsLayoutWidgetWithKeySignal(size=WINDOW_SIZE)
    window.setLayout(layout)
    window.setWindowTitle(f"{WINDOW_NAME}: {name or get_calling_scope_name()}")

    def main():
        add_image_views()
        add_actions()
        image_view_mapping = set_images(images, image_views)
        try:
            yield image_view_mapping, app, window, layout, button_layout
        finally:
            window.show()
            app.exec()

    def add_image_views():
        coords = GRIDS[num_views].coords
        for column in range(width):
            layout.setColumnStretch(column, 1)
        for coord in coords:
            image_view = get_image_view()
            layout.addWidget(image_view, *coord)
            image_views.append(image_view)

    def add_actions():
        window.key_signal.connect(keyPressEvent)
        layout.addLayout(button_layout, height, 0, 1, width)
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


# * -------------------------------------------------------------------------------- * #


def coerce_images(images: AllViewable) -> NamedViewable:
    """Coerce images to a mapping of title to image."""
    if isinstance(images, Mapping):
        images_ = images
    elif isinstance(images, np.ndarray):
        images_ = [images]
    elif isinstance(images, Sequence):
        # If given a sequence that could be a video or a set of images/videos to
        # compare, assume it is a video if it is too long to be a set of comparisons.
        largest_grid = 16
        if len(images) > largest_grid:
            try:
                images_ = [np.array(images)]
            except ValueError:
                images_ = images
        else:
            images_ = images
    else:
        raise TypeError(f"Unsupported type for images: {type(images)}")

    return (
        {title: np.array(value) for title, value in images_.items()}
        if isinstance(images_, Mapping)
        else {i: np.array(value) for i, value in enumerate(images_)}
    )


def set_images(
    images: NamedViewable, image_views: list[pg.ImageView]
) -> dict[str | int, pg.ImageView]:
    """Set images into the image views."""
    for (title, value), image_view in zip(images.items(), image_views, strict=False):
        if value.dtype == bool:
            value = scale_bool(value)
        image_view.setImage(value)
        if isinstance(title, str):
            image_view.addItem(pg.TextItem(title, fill=pg.mkBrush("black")))
    return dict(zip(images.keys(), image_views, strict=True))


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


def get_square_grid_coordinates(n: int) -> Iterator[ArrInt]:
    """Get the coordinates of a square grid."""
    x, y = np.indices((n, n))
    yield from np.column_stack((x.ravel(), y.ravel()))


# * -------------------------------------------------------------------------------- * #


def get_calling_scope_name():
    """Get the name of the calling scope."""
    current_frame = inspect.currentframe()
    scope_name = current_frame.f_back.f_code.co_name  # type: ignore
    while scope_name in {
        "image_viewer",
        "view_images",
        "preview_images",
        "__enter__",
        "eval_in_context",
        "evaluate_expression",
        "_run_with_interrupt_thread",
        "_run_with_unblock_threads",
        "new_func",
        "internal_evaluate_expression_json",
        "do_it",
        "process_internal_commands",
    }:
        current_frame = current_frame.f_back  # type: ignore
        scope_name = current_frame.f_back.f_code.co_name  # type: ignore
    return scope_name
