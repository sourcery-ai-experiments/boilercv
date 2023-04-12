from collections.abc import Sequence

import cv2 as cv
import numpy as np

from boilercv.colors import WHITE, WHITE3
from boilercv.images import unpad
from boilercv.types import ArrFloat, ArrInt, Img, ImgBool


def convert_image(img: Img, code: int | None = None) -> Img:
    """Convert image format, handling inconsistent type annotations."""
    return cv.cvtColor(img, code)  # type: ignore


def apply_mask(img: Img, mask: Img) -> Img:
    """Mask an image, keeping parts where the mask is bright."""
    return cv.add(img, cv.bitwise_not(mask))


def pad(img: Img, pad_width: int, value: int) -> Img:
    """Pad an image. Faster than np.pad()."""
    return cv.copyMakeBorder(
        img,
        top=pad_width,
        bottom=pad_width,
        left=pad_width,
        right=pad_width,
        borderType=cv.BORDER_CONSTANT,
        value=value,
    )


def binarize(img: Img, block_size: int = 11, thresh_dist_from_mean: int = 2) -> ImgBool:
    """Binarize an image with an adaptive threshold."""
    block_size += 1 if block_size % 2 == 0 else 0
    return cv.adaptiveThreshold(
        src=img,
        maxValue=np.iinfo(img.dtype).max,
        adaptiveMethod=cv.ADAPTIVE_THRESH_MEAN_C,
        thresholdType=cv.THRESH_BINARY,
        blockSize=block_size,
        C=thresh_dist_from_mean,
    ).astype(bool)


def flood(img: Img) -> ImgBool:
    """Flood the image, returning the resulting flood as a bright mask."""
    seed_point = np.array(img.shape) // 2
    max_value = np.iinfo(img.dtype).max
    # OpenCV needs a masked array with a one-pixel pad
    pad_width = 1
    mask = pad(np.zeros_like(img), pad_width, value=1)
    _retval, _image, mask, _rect = cv.floodFill(
        image=img,
        mask=mask,
        seedPoint=seed_point,
        newVal=None,  # Ignored in mask only mode
        flags=cv.FLOODFILL_MASK_ONLY,
    )
    # Return the mask in original dimensions
    return unpad(mask, pad_width).astype(bool)


def get_roi(wall: Img) -> Img:
    """Erode the wall to get the ROI."""
    kernel_size = 9
    close_kernel_size = 4
    kernel = cv.getStructuringElement(cv.MORPH_ELLIPSE, [kernel_size] * 2)
    close_kernel = cv.getStructuringElement(cv.MORPH_ELLIPSE, [close_kernel_size] * 2)
    # Explicitly pad out the image since cv.morphologyEx boundary handling is weird
    pad_width = max(close_kernel_size, kernel_size)
    padded = pad(wall, pad_width, value=0)
    wall = cv.morphologyEx(src=padded, op=cv.MORPH_CLOSE, kernel=close_kernel)
    roi = cv.morphologyEx(src=wall, op=cv.MORPH_ERODE, kernel=kernel)
    return unpad(roi, pad_width).astype(bool)


def get_wall(roi: Img) -> Img:
    """Dilate the ROI to get the wall."""
    # Explicitly pad out the image since cv.morphologyEx boundary handling is weird
    kernel_size = 9
    kernel = cv.getStructuringElement(cv.MORPH_ELLIPSE, [kernel_size] * 2)
    pad_width = kernel_size
    padded = pad(roi, pad_width, value=0)
    wall = cv.morphologyEx(src=padded, op=cv.MORPH_DILATE, kernel=kernel)
    return unpad(wall, pad_width).astype(bool)


def build_mask_from_polygons(img: Img, contours: Sequence[ArrInt]) -> Img:
    """Build a mask from the intersection of a sequence of polygonal contours."""
    # OpenCV expects contours as shape (N, 1, 2) instead of (N, 2)
    contours = [np.fliplr(contour).reshape(-1, 1, 2) for contour in contours]
    blank = np.zeros_like(img)
    return cv.fillPoly(
        img=blank,
        pts=contours,  # Expects a list of coordinates, we have just one
        color=WHITE3,
    )


def find_contours(img: Img, method: int = cv.CHAIN_APPROX_NONE) -> list[ArrInt]:
    """Find external contours of bright objects in an image."""
    contours, _hierarchy = cv.findContours(
        image=img,
        mode=cv.RETR_EXTERNAL,  # No hierarchy needed because we keep external contours
        method=method,
    )
    # Despite images having dims (y, x) and shape (h, w), OpenCV returns contours with
    # dims (point, 1, pair), where dim "pair" has coords (x, y).
    contours = [np.fliplr(contour.reshape(-1, 2)) for contour in contours]
    return contours


def draw_contours(
    img: Img,
    contours: Sequence[ArrInt],
    contour_index: int = -1,
    thickness: int = -1,
    color: int | tuple[int, ...] = WHITE,
) -> Img:
    """Draw contours on an image."""
    # OpenCV expects contours as shape (N, 1, 2) instead of (N, 2)
    contours = [np.fliplr(contour).reshape(-1, 1, 2) for contour in contours]
    return cv.drawContours(
        image=img,
        contours=contours,
        contourIdx=contour_index,
        color=color,
        thickness=thickness,
    )


def find_line_segments(img: Img) -> tuple[ArrFloat, cv.LineSegmentDetector]:
    """Find line segments in an image."""
    lsd = cv.createLineSegmentDetector()
    lines, *_ = lsd.detect(img)
    # OpenCV returns line segments as shape (N, 1, 4) instead of (N, 4)
    lines = lines.reshape(-1, 4)
    return lines, lsd
