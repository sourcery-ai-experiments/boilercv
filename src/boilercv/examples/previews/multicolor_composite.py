"""Overlay detected bubbles on the gray stage."""

from itertools import cycle

import cv2 as cv
import numpy as np
import seaborn as sns
from matplotlib import pyplot as plt

from boilercv import DEBUG, PREVIEW, WRITE
from boilercv.captivate.captures import write_image
from boilercv.captivate.previews import view_images
from boilercv.data import VIDEO
from boilercv.data.sets import get_contours_df, get_dataset
from boilercv.examples.previews import _EXAMPLE
from boilercv.images import overlay
from boilercv.images.cv import convert_image, draw_contours
from boilercv.models.params import LOCAL_PATHS
from boilercv.types import ArrInt

_NUM_FRAMES = 1

_PALETTE = [c for c in sns.color_palette("Set1") if not c[0] == c[1] == c[2]]  # type: ignore
_PALETTE_CV = [(int(255 * c[2]), int(255 * c[1]), int(255 * c[0])) for c in _PALETTE]


def main():
    frame = _NUM_FRAMES - 1
    gray = (
        get_dataset(_EXAMPLE, _NUM_FRAMES, stage="large_sources")[VIDEO]
        .isel(frame=frame)
        .values
    )
    contours: list[ArrInt] = list(
        get_contours_df(_EXAMPLE)
        .loc[frame, :]
        .groupby("contour")
        .apply(lambda grp: grp.values)
    )
    highlighted = np.zeros_like(convert_image(gray, cv.COLOR_GRAY2BGR))
    for contour, color in zip(contours, cycle(_PALETTE_CV), strict=False):
        highlighted = draw_contours(highlighted, [contour], color=color)
    highlighted = convert_image(highlighted, cv.COLOR_BGR2RGB)
    composed = overlay(gray, highlighted, alpha=0.7)
    if PREVIEW:
        if DEBUG:
            sns.palplot(_PALETTE)
        plt.show()
        view_images(composed)
    if WRITE:
        path = LOCAL_PATHS.media / "examples" / _EXAMPLE / "multicolor"
        path.parent.mkdir(parents=True, exist_ok=True)
        write_image(path, composed)


if __name__ == "__main__":
    main()
