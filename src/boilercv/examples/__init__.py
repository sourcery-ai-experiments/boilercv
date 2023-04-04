"""Examples, experiments, and demonstrations."""

from collections.abc import Iterator
from pathlib import Path

import cv2 as cv
import xarray as xr

from boilercv.data import VIDEO
from boilercv.models.params import PARAMS
from boilercv.types import DA, Img

EXAMPLE_VIDEO_NAME = "2022-11-30T13-41-00"
SOURCE = PARAMS.paths.examples / f"{EXAMPLE_VIDEO_NAME}.nc"
NUM_FRAMES = 300
# TODO: Source the ROI from the dataset.
EXAMPLE_ROI = PARAMS.paths.examples / f"{EXAMPLE_VIDEO_NAME}_roi.yaml"


def get_images() -> DA:
    with xr.open_dataset(SOURCE) as ds:
        return ds[VIDEO].sel(frame=slice(None, NUM_FRAMES))


EXAMPLE_VIDEO = get_images()
EXAMPLE_FRAME_LIST = list(EXAMPLE_VIDEO.values)


def capture_images(path: Path) -> Iterator[Img]:
    """Images from a video file."""
    video_capture = cv.VideoCapture(str(path))
    while True:
        read_is_successful, image = video_capture.read()
        if not read_is_successful:
            break
        yield image
