"""Contour-finding examples."""

import xarray as xr

from boilercv import get_8bit_images
from boilercv.models.params import PARAMS

with xr.open_dataset(PARAMS.paths.sources / "results_2022-01-06T13-23-39.nc") as ds:
    IMAGES = get_8bit_images(ds.images.data)

ROI_FILE = PARAMS.paths.examples / "roi.yaml"
