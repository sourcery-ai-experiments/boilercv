"""Show an OpenCV sample image."""

import cv2 as cv

from boilercv import PREVIEW
from boilercv.captivate.previews import view_images
from boilercv.types import ImgLike


def main(preview=PREVIEW) -> ImgLike:
    img = cv.cvtColor(
        cv.imread(cv.samples.findFile("starry_night.jpg")), cv.COLOR_BGR2RGB
    )
    if preview:
        view_images(img)
    return img


if __name__ == "__main__":
    main()
