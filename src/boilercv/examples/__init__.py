"""Examples, experiments, and demonstrations."""

from collections.abc import Iterator
from pathlib import Path

import cv2 as cv

from boilercv.types import Img


def capture_images(path: Path) -> Iterator[Img]:
    """Images from a video file."""
    video_capture = cv.VideoCapture(str(path))
    while True:
        read_is_successful, image = video_capture.read()
        if not read_is_successful:
            break
        yield image
