"""Preview a video."""

from pathlib import Path

import cv2 as cv
import numpy as np

from boilercv.examples import capture_images
from boilercv.gui import preview_images
from boilercv.images import convert_image


def main():
    images = capture_images(Path(cv.samples.findFile("vtest.avi")))
    video = np.stack([convert_image(image, cv.COLOR_BGR2RGB) for image in images])
    preview_images(video)


if __name__ == "__main__":
    main()
