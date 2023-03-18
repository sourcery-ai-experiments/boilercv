from pathlib import Path

import cv2 as cv
import numpy as np
import yaml

from boilercv import MARKER_COLOR, WHITE, convert_image
from boilercv.types import ArrIntDef, Img, NBit_T


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


def mask(image: Img[NBit_T], roi: ArrIntDef) -> Img[NBit_T]:
    blank = np.zeros_like(image)
    mask: Img[NBit_T] = ~cv.fillPoly(
        img=blank,
        pts=[roi],  # Needs a list of arrays
        color=WHITE,
    )
    return cv.add(image, mask)


def threshold(image: Img[NBit_T]) -> Img[NBit_T]:
    return cv.adaptiveThreshold(
        src=image,
        maxValue=np.iinfo(image.dtype).max,
        adaptiveMethod=cv.ADAPTIVE_THRESH_MEAN_C,
        thresholdType=cv.THRESH_BINARY,
        blockSize=11,
        C=2,
    )


def find_contours(image: Img[NBit_T]) -> list[ArrIntDef]:
    (contours, _) = cv.findContours(
        image=~image, mode=cv.RETR_EXTERNAL, method=cv.CHAIN_APPROX_SIMPLE
    )
    return contours


def draw_contours(image: Img[NBit_T], contours, thickness=2) -> Img[NBit_T]:
    # Need three-channel image to paint colored contours
    three_channel_gray = convert_image(image, cv.COLOR_GRAY2RGB)
    # ! Careful: cv.drawContours modifies in-place AND returns
    return cv.drawContours(
        image=three_channel_gray,
        contours=contours,
        contourIdx=-1,
        color=MARKER_COLOR,
        thickness=thickness,
    )
