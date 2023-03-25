"""Image acquisition and processing."""

from functools import wraps
from pathlib import Path
from typing import Literal

import cv2 as cv
import numpy as np
import yaml

from boilercv import MARKER_COLOR, WHITE
from boilercv.types import ArrInt

# TODO: Now that our type system is simpler, see if this can be typed better


def cv_func(func):
    """Convert first argument to 8-bit for functions that use OpenCV internally."""

    @wraps(func)
    def wrapper(image, *args, **kwargs):
        return func(image.astype(np.uint8), *args, **kwargs)

    return wrapper


def load_roi(
    image: ArrInt,
    roi_path: Path,
    roi_type: Literal["poly", "line"] = "poly",
) -> ArrInt:
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


@cv_func
def mask(image: ArrInt, roi: ArrInt) -> ArrInt:
    blank = np.zeros_like(image)
    mask: ArrInt = ~cv.fillPoly(
        img=blank,
        pts=[roi],  # Needs a list of arrays
        color=WHITE,
    )
    return cv.add(image, mask)


@cv_func
def threshold(
    image: ArrInt, block_size: int = 11, thresh_dist_from_mean: int = 2
) -> ArrInt:
    block_size += 1 if block_size % 2 == 0 else 0
    return cv.adaptiveThreshold(
        src=image,
        maxValue=np.iinfo(image.dtype).max,
        adaptiveMethod=cv.ADAPTIVE_THRESH_MEAN_C,
        thresholdType=cv.THRESH_BINARY,
        blockSize=block_size,
        C=thresh_dist_from_mean,
    )


@cv_func
def find_contours(image: ArrInt) -> list[ArrInt]:
    """Find external contours of dark objects in an image."""
    # Invert the default of finding bright contours since bubble edges are dark
    image = ~image
    contours, _hierarchy = cv.findContours(
        image=image,
        mode=cv.RETR_EXTERNAL,  # No hierarchy needed because we keep external contours
        method=cv.CHAIN_APPROX_SIMPLE,  # Approximate the contours
    )
    # OpenCV returns contours as shape (N, 1, 2) instead of (N, 2)
    contours = [contour.reshape(-1, 2) for contour in contours]
    return contours


@cv_func
def draw_contours(
    image: ArrInt, contours: list[ArrInt], contour_index: int = -1, thickness=2
) -> ArrInt:
    # OpenCV expects contours as shape (N, 1, 2) instead of (N, 2)
    contours = [contour.reshape(-1, 1, 2) for contour in contours]
    # Need three-channel image to paint colored contours
    three_channel_gray = convert_image(image, cv.COLOR_GRAY2RGB)
    return cv.drawContours(
        image=three_channel_gray,
        contours=contours,
        contourIdx=contour_index,
        color=MARKER_COLOR,
        thickness=thickness,
    )


@cv_func
def flood(image: ArrInt, seed_point: tuple[int, int]) -> ArrInt:
    """Flood the image, returning the resulting flood as a mask."""
    max_value = np.iinfo(image.dtype).max
    mask = np.pad(
        np.full_like(image, 0),
        pad_width=1,
        constant_values=max_value,
    )
    _retval, _image, mask, _rect = cv.floodFill(
        image=image,
        mask=mask,
        seedPoint=seed_point,
        newVal=None,  # Ignored in mask only mode
        flags=cv.FLOODFILL_MASK_ONLY,
    )
    return mask[1:-1, 1:-1].astype(np.bool_)


# * -------------------------------------------------------------------------------- * #


def convert_image(image: ArrInt, code: int | None = None) -> ArrInt:
    """Convert image format, handling inconsistent type annotations."""
    return image if code is None else cv.cvtColor(image, code)  # type: ignore
