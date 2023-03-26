"""Image acquisition and processing."""


from collections.abc import Sequence

import cv2 as cv
import numpy as np

from boilercv import MARKER_COLOR, WHITE, npa
from boilercv.types import ArrFloat, ArrInt, Img


def convert_image(img: Img, code: int | None = None) -> Img:
    """Convert image format, handling inconsistent type annotations."""
    return img if code is None else cv.cvtColor(img, code)  # type: ignore


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
    """Flood the image, returning the resulting flood as a mask."""
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


def close_and_erode(img: Img) -> Img:
    """Close small holes and erode the outer boundary of an ROI."""

    # Explicitly pad out the image since cv.morphologyEx boundary handling is weird
    close_size = 4
    erode_size = 9
    pad_width = max(close_size, erode_size)
    padded = pad(img, pad_width, value=0)

    # Close small holes inside the ROI
    closed = cv.morphologyEx(
        src=padded,
        op=cv.MORPH_CLOSE,
        kernel=cv.getStructuringElement(cv.MORPH_ELLIPSE, (close_size, close_size)),
    )

    # Erode ROI boundaries
    erode_size = 9
    eroded = cv.morphologyEx(
        src=closed,
        op=cv.MORPH_ERODE,
        kernel=cv.getStructuringElement(cv.MORPH_ELLIPSE, (erode_size, erode_size)),
    )

    return unpad(eroded, pad_width)


def find_contours(img: Img) -> list[ArrInt]:
    """Find external contours of dark objects in an image."""
    # Invert the default of finding bright contours since bubble edges are dark
    img = ~img
    contours, _hierarchy = cv.findContours(
        image=img,
        mode=cv.RETR_EXTERNAL,  # No hierarchy needed because we keep external contours
        method=cv.CHAIN_APPROX_SIMPLE,  # Approximate the contours
    )
    # OpenCV returns contours as shape (N, 1, 2) instead of (N, 2)
    contours = [contour.reshape(-1, 2) for contour in contours]
    return contours


def mask(img: Img, rois: Sequence[ArrInt]) -> Img:
    """Mask an image bounded by one or more polygonal regions of interest."""
    blank = np.zeros_like(img)
    # Fill a polygon to make the ROI bright, invert this to make the ROI dark
    mask: Img = ~cv.fillPoly(
        img=blank,
        pts=rois,  # Expects a list of coordinates, we have just one
        color=WHITE,
    )
    # OpenCV saturates on addition, keeping only the ROI
    return cv.add(img, mask)


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
