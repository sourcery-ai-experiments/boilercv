"""Contour-finding examples."""

from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

import cv2 as cv

from boilercv.types import Img, NBit

ESC_KEY = ord("\x1b")


@contextmanager
def video_capture_images(path: Path) -> Iterator[Iterator[Img[NBit]]]:
    """Images from a video file."""
    video_capture = cv.VideoCapture(str(path))
    try:
        yield get_video_capture_images(video_capture)
    finally:
        video_capture.release()


def get_video_capture_images(video_capture: cv.VideoCapture) -> Iterator[Img[NBit]]:
    """Images from a video file."""
    while True:
        read_is_successful, image = video_capture.read()
        if not read_is_successful:
            break
        yield image
