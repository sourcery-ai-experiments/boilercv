"""Image acquisition and processing."""

# * Pure numpy image processing functions take lots of types, including DataArrays.
# pyright: reportGeneralTypeIssues=none

from typing import Any

import numpy as np
from matplotlib.font_manager import FontProperties, findfont
from numpy import typing as npt
from PIL import Image, ImageDraw, ImageFont, ImageOps

from boilercv import DEBUG
from boilercv.colors import BLACK, BLACK3, RED, WHITE, WHITE3
from boilercv.types import Img, ImgLike, T

if DEBUG:
    from PIL import ImageShow  # noqa: F401

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
    """Draw text in the top-right corner of an image.

    Args:
        image: Image.
        text: Text to draw.
    """
    if image.ndim == 3:
        rectangle_fill = BLACK3
        font_fill = WHITE3
    else:
        rectangle_fill = BLACK
        font_fill = WHITE
    _, image_width = image.shape[:2]
    pil_image = Image.fromarray(image)
    _, _, font_bbox_width, font_bbox_height = FONT.getbbox(text)
    text_p0 = (image_width - PAD - font_bbox_width, PAD)
    p0 = (text_p0[0] - PAD, text_p0[1] - PAD)
    p1 = (text_p0[0] + PAD + font_bbox_width, text_p0[1] + PAD + font_bbox_height)
    draw = ImageDraw.Draw(pil_image)
    draw.rectangle((p0, p1), fill=rectangle_fill)
    draw.text(text_p0, text, font=FONT, fill=font_fill)
    return np.asarray(pil_image)


def overlay(
    image: ImgLike,
    overlay: ImgLike,
    color: tuple[int, int, int] = RED,
    alpha: float = 0.3,
) -> Img:
    """Color an image given an overlay.

    Args:
        image: Image.
        overlay: Overlay image.
        color: Color for the overlay.
        alpha: Alpha value for the overlay. Range: 0-1
    """
    background = Image.fromarray(image).convert("RGBA")
    objects = Image.fromarray(overlay)
    if overlay.ndim == 2:
        objects = ImageOps.colorize(objects, WHITE3, color)
        mask = Image.fromarray(~(overlay * alpha).astype(np.uint8))
    else:
        mask = Image.fromarray(
            ~(bool(np.mean(overlay, axis=-1)) * alpha).astype(np.uint8)
        )
    composite = Image.composite(background, objects, mask)
    return np.asarray(composite)
