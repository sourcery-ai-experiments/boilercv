"""Image acquisition and processing."""


from collections.abc import Sequence

import cv2 as cv
import numpy as np

from boilercv import MARKER_COLOR, WHITE, npa
from boilercv.types import ArrFloat, ArrInt, Img


def convert_image(img: Img, code: int | None = None) -> Img:
    """Convert image format, handling inconsistent type annotations."""
    return img if code is None else cv.cvtColor(img, code)  # type: ignore


def apply_mask(img: Img, mask: Img) -> Img:
    """Mask an image, keeping parts where the mask is bright."""
    return cv.add(img, ~mask)


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


def unpad(img: Img, pad_width: int) -> Img:
    """Remove padding from an image."""
    return img[pad_width:-pad_width, pad_width:-pad_width]


def binarize(img: Img, block_size: int = 11, thresh_dist_from_mean: int = 2) -> Img:
    """Binarize an image with an adaptive threshold."""
    block_size += 1 if block_size % 2 == 0 else 0
    return cv.adaptiveThreshold(
        src=img,
        maxValue=np.iinfo(img.dtype).max,
        adaptiveMethod=cv.ADAPTIVE_THRESH_MEAN_C,
        thresholdType=cv.THRESH_BINARY,
        blockSize=block_size,
        C=thresh_dist_from_mean,
    )


def flood(img: Img) -> Img:
    """Flood the image, returning the resulting flood as a bright mask."""
    seed_point = npa(img.shape) // 2
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
    # Return the mask in original dimensions, maxing out the values
    return unpad(mask, pad_width) * max_value


def morph(img: Img) -> tuple[Img, Img]:
    """Close small holes and return the ROI both eroded and dilated as bright masks."""

    # Explicitly pad out the image since cv.morphologyEx boundary handling is weird
    kernel_size = 9
    close_kernel_size = 4
    kernel = cv.getStructuringElement(cv.MORPH_ELLIPSE, [kernel_size] * 2)
    close_kernel = cv.getStructuringElement(cv.MORPH_ELLIPSE, [close_kernel_size] * 2)
    pad_width = max(close_kernel_size, kernel_size)
    padded = pad(img, pad_width, value=0)

    # Erode and dilate a bright region
    closed = cv.morphologyEx(src=padded, op=cv.MORPH_CLOSE, kernel=close_kernel)
    eroded = cv.morphologyEx(src=closed, op=cv.MORPH_ERODE, kernel=kernel)
    dilated = cv.morphologyEx(src=closed, op=cv.MORPH_DILATE, kernel=kernel)

    return tuple(unpad(image, pad_width) for image in [closed, eroded, dilated])


def find_contours(img: Img) -> list[ArrInt]:
    """Find external contours of bright objects in an image."""
    contours, _hierarchy = cv.findContours(
        image=img,
        mode=cv.RETR_EXTERNAL,  # No hierarchy needed because we keep external contours
        method=cv.CHAIN_APPROX_NONE,  # Approximate the contours
    )
    # Despite images having dims (y, x) and shape (h, w), OpenCV returns contours with
    # dims (point, 1, pair), where dim "pair" has coords (x, y).
    contours = [np.fliplr(contour.squeeze()) for contour in contours]
    return contours


def build_mask_from_polygons(img: Img, contours: Sequence[ArrInt]) -> Img:
    """Build a mask from the intersection of a sequence of polygonal contours."""
    # OpenCV expects contours as shape (N, 1, 2) instead of (N, 2)
    contours = [np.fliplr(contour).reshape(-1, 1, 2) for contour in contours]
    blank = np.zeros_like(img)
    return cv.fillPoly(
        img=blank,
        pts=contours,  # Expects a list of coordinates, we have just one
        color=WHITE,
    )


def draw_contours(
    img: Img, contours: Sequence[ArrInt], contour_index: int = -1, thickness=2
) -> Img:
    """Draw contours on an image."""
    # OpenCV expects contours as shape (N, 1, 2) instead of (N, 2)
    contours = [contour.reshape(-1, 1, 2) for contour in contours]
    # Need three-channel image to paint colored contours
    three_channel_gray = convert_image(img, cv.COLOR_GRAY2RGB)
    return cv.drawContours(
        image=three_channel_gray,
        contours=contours,
        contourIdx=contour_index,
        color=MARKER_COLOR,
        thickness=thickness,
    )


def find_line_segments(img: Img) -> tuple[ArrFloat, cv.LineSegmentDetector]:
    """Find line segments in an image."""
    lsd = cv.createLineSegmentDetector()
    lines, *_ = lsd.detect(img)
    # OpenCV returns line segments as shape (N, 1, 4) instead of (N, 4)
    lines = lines.reshape(-1, 4)
    return lines, lsd
