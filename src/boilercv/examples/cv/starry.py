"""Show an OpenCV sample image."""

from cv2 import COLOR_BGR2RGB, cvtColor, imread
from cv2.samples import findFile

from boilercv import PREVIEW
from boilercv.captivate.previews import view_images
from boilercv.types import ImgLike


def main(preview=PREVIEW) -> ImgLike:
    img = cvtColor(imread(findFile("starry_night.jpg")), COLOR_BGR2RGB)
    if preview:
        view_images(img)
    return img


if __name__ == "__main__":
    main()
