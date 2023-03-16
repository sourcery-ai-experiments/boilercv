"""Preview a video."""


from pathlib import Path

import cv2 as cv
import numpy as np

from boilercv import qt_window
from boilercv.examples import bgr_to_rgb
from boilercv.examples.contours import video_capture_images
from boilercv.examples.contours.pyqtgraph_cine import get_roi


def main():
    with video_capture_images(Path(cv.samples.findFile("vtest.avi"))) as images:
        video = np.stack([bgr_to_rgb(image) for image in images])
    with qt_window() as (app, window):
        get_roi(video, app, window)


if __name__ == "__main__":
    main()
