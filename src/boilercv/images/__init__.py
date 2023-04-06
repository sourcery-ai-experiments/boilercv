"""Image acquisition and processing."""

# * Pure numpy image processing functions take lots of types, including DataArrays.
# pyright: reportGeneralTypeIssues=none

from collections.abc import Iterator
from pathlib import Path
from typing import Any

import cv2 as cv
import numpy as np
from matplotlib.font_manager import FontProperties, findfont
from numpy import typing as npt
from PIL import Image, ImageDraw, ImageFont

from boilercv.colors import BLACK, WHITE
from boilercv.types import Img, ImgLike, T

# * -------------------------------------------------------------------------------- * #
# * PURE NUMPY - TYPE PRESERVING


def scale_float(img: T, dtype: npt.DTypeLike = np.uint8) -> T:
    """Return the input as `dtype` multiplied by the max value of `dtype`.

    Useful for scaling float-valued arrays to integer-valued images.
    """
    scaled = (img - img.min()) / (img.max() - img.min())
    return scaled.astype(dtype) * np.iinfo(dtype).max


def unpad(img: T, pad_width: int) -> T:
    """Remove padding from an image."""
    return img[pad_width:-pad_width, pad_width:-pad_width]


# * -------------------------------------------------------------------------------- * #
# * PURE NUMPY - NOT ALWAYS TYPE PRESERVING


def scale_bool(img: Any, dtype: npt.DTypeLike = np.uint8) -> Any:
    """Return the input as `dtype` multiplied by the max value of `dtype`.

    Useful for functions (such as in OpenCV) which expect numeric bools.
    """
    return img.astype(dtype) * np.iinfo(dtype).max


# * -------------------------------------------------------------------------------- * #
# * OTHER - NOT ALWAYS TYPE PRESERVING

FONT = ImageFont.truetype(findfont(FontProperties(family="dejavu sans")), 24)
PAD = 10


def draw_text(image: ImgLike, text: str = "") -> ImgLike:
    """Draw text in the top-left corner of an image.

    Args:
        image: Image.
        text: Text to draw.
    """
    pil_image = Image.fromarray(image)
    _, _, right, bottom = FONT.getbbox(text)
    text_p0 = (PAD,) * 2
    p0 = (text_p0[0] - PAD, text_p0[1] - PAD)
    p1 = (text_p0[0] + PAD + right, text_p0[1] + PAD + bottom)
    draw = ImageDraw.Draw(pil_image)
    draw.rectangle((p0, p1), fill=BLACK)
    draw.text(text_p0, text, font=FONT, fill=WHITE)
    return np.asarray(pil_image)


# * -------------------------------------------------------------------------------- * #
# * VIDEO CAPTURE FUNCTIONS


def capture_images(path: Path) -> Iterator[Img]:
    """Load images from a video file."""
    video_capture = cv.VideoCapture(str(path))
    while True:
        read_is_successful, image = video_capture.read()
        if not read_is_successful:
            break
        yield image
