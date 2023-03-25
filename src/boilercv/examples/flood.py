"""Flood the maximum across frames to establish a region of interest.

Although the OpenCV approach requires more boilerplate, it is faster than the skimage
approach.
"""


import cv2 as cv
import numpy as np
from skimage.morphology import flood as flood_  # We define our own

from boilercv import EXAMPLE_BIG_CINE, IMAGES
from boilercv.data import prepare_dataset
from boilercv.gui import compare_images, save_roi
from boilercv.images import draw_contours, find_contours, flood, threshold
from boilercv.models.params import PARAMS
from boilercv.types import ArrInt

NUM_FRAMES = 100
ROI_FILE = PARAMS.paths.examples / "roi_auto.yaml"
KERNEL_SIZE = 9
DRAWN_CONTOUR_THICKNESS = 2


def main():
    source = EXAMPLE_BIG_CINE
    dataset = prepare_dataset(source, NUM_FRAMES)
    images = dataset[IMAGES]
    maximum: ArrInt = images.max("frames").data
    binarized = threshold(maximum)
    (height, width) = maximum.shape
    midpoint = (height // 2, width // 2)
    flooded = flood(binarized, midpoint)
    flooded8: ArrInt = flooded.astype(np.uint8)
    kernel = np.ones((KERNEL_SIZE, KERNEL_SIZE), np.uint8)
    eroded = cv.erode(flooded8, kernel)
    contours = find_contours(~eroded)
    if len(contours) > 1:
        raise ValueError("More than one contour found when searching for the ROI.")
    roi = contours[0]
    first_image = images.isel(frames=0).values
    contoured = draw_contours(first_image, [roi], thickness=DRAWN_CONTOUR_THICKNESS)
    save_roi(roi, ROI_FILE)
    # flooded_skim = flood_skim(binarized, midpoint)
    # pixel_difference_rate = (
    #     np.logical_xor(flooded, flooded_skim).sum() / flooded.size
    # )
    # print(f"{pixel_difference_rate=}")
    compare_images(
        dict(
            maximum=maximum,
            binarized=binarized,
            eroded=eroded,
            # flooded_skim=flooded_skim,
            contoured=contoured,
        )
    )


def flood_skim(image: ArrInt, seed_point: tuple[int, int]) -> ArrInt:
    """Flood the image, returning the resulting flood as a mask."""
    return flood_(
        image,
        seed_point,
        connectivity=0,
    )


if __name__ == "__main__":
    main()
