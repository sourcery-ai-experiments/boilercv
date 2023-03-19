"""Contour-finding examples."""

from boilercv import get_8bit_images
from boilercv.gui import get_video_images
from boilercv.models.params import PARAMS

IMAGES = get_8bit_images(
    get_video_images(PARAMS.paths.examples / "results_2022-11-30T12-39-07_98C.cine")
)
