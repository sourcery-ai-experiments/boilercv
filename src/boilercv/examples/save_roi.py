"""Save the ROI to a legacy YAML format."""

from warnings import warn

import cv2 as cv

from boilercv.captivate.previews import save_roi
from boilercv.data import apply_to_img_da
from boilercv.data.sets import get_dataset
from boilercv.examples import EXAMPLE_ROI, EXAMPLE_VIDEO_NAME
from boilercv.images import scale_bool
from boilercv.images.cv import find_contours, get_wall
from boilercv.types import DA


def main():
    ds = get_dataset(EXAMPLE_VIDEO_NAME)
    roi = ds["roi"]
    wall: DA = apply_to_img_da(get_wall, scale_bool(roi), name="wall")
    contours = find_contours(scale_bool(wall.values), method=cv.CHAIN_APPROX_SIMPLE)
    if len(contours) > 1:
        warn("More than one contour found when searching for the ROI.", stacklevel=1)
    save_roi(contours[0], EXAMPLE_ROI)
