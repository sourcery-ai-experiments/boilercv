"""Preview a video."""


from pathlib import Path

import cv2 as cv
import numpy as np

from boilercv.examples import bgr_to_rgb, video_images
from boilercv.examples.contours.pyqtgraph_cine import get_roi


def main():
    with video_images(Path(cv.samples.findFile("vtest.avi"))) as images:
        video = np.stack([bgr_to_rgb(image) for image in images])
    get_roi(video)


if __name__ == "__main__":
    main()
