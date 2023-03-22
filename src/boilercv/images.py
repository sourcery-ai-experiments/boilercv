"""Image acquisition and processing."""

from pathlib import Path
from typing import Literal

import cv2 as cv
import numpy as np
import yaml

from boilercv import MARKER_COLOR, WHITE, convert_image
from boilercv.types import ArrIntDef, Img, NBit_T


def load_roi(
    image: Img[NBit_T],
    roi_path: Path,
    roi_type: Literal["poly", "line"] = "poly",
) -> ArrIntDef:
    """Load the region of interest for an image."""
    (width, height) = image.shape[-2:]
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


def mask(image: Img[NBit_T], roi: ArrIntDef) -> Img[NBit_T]:
    blank = np.zeros_like(image)
    mask: Img[NBit_T] = ~cv.fillPoly(
        img=blank,
        pts=[roi],  # Needs a list of arrays
        color=WHITE,
    )
    return cv.add(image, mask)


def threshold(
    image: Img[NBit_T], block_size: int = 11, thresh_dist_from_mean: int = 2
) -> Img[NBit_T]:
    block_size += 1 if block_size % 2 == 0 else 0
    return cv.adaptiveThreshold(
        src=image,
        maxValue=np.iinfo(image.dtype).max,
        adaptiveMethod=cv.ADAPTIVE_THRESH_MEAN_C,
        thresholdType=cv.THRESH_BINARY,
        blockSize=block_size,
        C=thresh_dist_from_mean,
    )


def find_contours(image: Img[NBit_T]) -> list[ArrIntDef]:
    (contours, _) = cv.findContours(
        image=~image, mode=cv.RETR_EXTERNAL, method=cv.CHAIN_APPROX_SIMPLE
    )
    return contours


def draw_contours(
    image: Img[NBit_T], contours: list[ArrIntDef], contour_index: int = -1, thickness=2
) -> Img[NBit_T]:
    # Need three-channel image to paint colored contours
    three_channel_gray = convert_image(image, cv.COLOR_GRAY2RGB)
    # ! Careful: cv.drawContours modifies in-place AND returns
    return cv.drawContours(
        image=three_channel_gray,
        contours=contours,
        contourIdx=contour_index,
        color=MARKER_COLOR,
        thickness=thickness,
    )
