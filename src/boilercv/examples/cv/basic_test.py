"""Preview a video."""

from pathlib import Path

from cv2 import COLOR_BGR2RGB
from cv2.samples import findFile
from numpy import stack

from boilercv import PREVIEW
from boilercv.captivate.previews import view_images
from boilercv.examples.cv import capture_images
from boilercv.images.cv import convert_image
from boilercv.types import Vid


def main(preview: bool = PREVIEW) -> Vid:
    images = capture_images(Path(findFile("vtest.avi")))
    video = stack([convert_image(image, COLOR_BGR2RGB) for image in images])
    if preview:
        view_images(video)
    return video


if __name__ == "__main__":
    main()
