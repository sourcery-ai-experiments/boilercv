"""Preview a video."""


from pathlib import Path

import cv2 as cv
import numpy as np

from boilercv.examples import bgr_to_rgb, interact_with_video, video_images


def main():
    with video_images(Path(cv.samples.findFile("vtest.avi"))) as images:
        video = np.stack([bgr_to_rgb(image) for image in images])
    interact_with_video(video)


if __name__ == "__main__":
    main()
