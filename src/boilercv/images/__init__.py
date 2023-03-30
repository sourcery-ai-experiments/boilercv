"""Image acquisition and processing."""

# Pure numpy image processing functions take lots of types, including DataArrays.
# pyright: reportGeneralTypeIssues=none

from typing import Any

import numpy as np
from numpy import typing as npt

from boilercv.types import T

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
