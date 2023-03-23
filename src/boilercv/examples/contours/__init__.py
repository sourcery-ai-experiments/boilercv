"""Contour-finding examples."""

from boilercv.data import prepare_images
from boilercv.models.params import PARAMS

NUM_FRAMES = 300


def get_images():
    source = PARAMS.paths.examples / "2022-11-30T13-41-00.cine"
    images, _ = prepare_images(source, num_frames=NUM_FRAMES)
    return list(images.values)


IMAGES = get_images()

ROI_FILE = PARAMS.paths.examples / "roi.yaml"
