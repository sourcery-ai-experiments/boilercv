"""Preview a video."""

from pathlib import Path

import cv2 as cv
import numpy as np

from boilercv import PREVIEW
from boilercv.captivate.previews import view_images
from boilercv.examples.cv import capture_images
from boilercv.images.cv import convert_image
from boilercv.types import Vid


def main(preview: bool = PREVIEW) -> Vid:
    images = capture_images(Path(cv.samples.findFile("vtest.avi")))
    video = np.stack([convert_image(image, cv.COLOR_BGR2RGB) for image in images])
    if preview:
        view_images(video)
    return video


if __name__ == "__main__":
    main()
