"""Flood the maximum across frames to establish a region of interest.

Although the OpenCV approach requires more boilerplate, it is faster than the skimage
approach.
"""

from pathlib import Path

import numpy as np
from skimage.morphology import flood as flood_  # We define our own

from boilercv import IMAGES
from boilercv.data import prepare_dataset
from boilercv.gui import compare_images
from boilercv.images import flood, threshold
from boilercv.types import Img, ImgBool8, NBit

NUM_FRAMES = 100


def main():
    source = Path("C:/Users/Blake/Desktop/2022-11-30T13-41-00.cine")
    dataset = prepare_dataset(source, NUM_FRAMES)
    images = dataset[IMAGES]
    maximum = images.max("frames").data
    binarized = threshold(maximum)
    (height, width) = maximum.shape
    midpoint = (height // 2, width // 2)
    flooded_cv = flood(binarized, midpoint)
    flooded_skim = flood_skim(binarized, midpoint)
    pixel_difference_rate = (
        np.logical_xor(flooded_cv, flooded_skim).sum() / flooded_cv.size
    )
    print(f"{pixel_difference_rate=}")
    compare_images([maximum, binarized, flooded_cv, flooded_skim])


def flood_skim(image: Img[NBit], seed_point: tuple[int, int]) -> ImgBool8:
    """Flood the image, returning the resulting flood as a mask."""
    return flood_(
        image,
        seed_point,
        connectivity=0,
    )


if __name__ == "__main__":
    main()
