"""Contour-finding examples."""

import xarray as xr

from boilercv import get_8bit_images
from boilercv.models.params import PARAMS

with xr.open_dataset(
    PARAMS.paths.examples / "results_2022-11-30T12-39-07_98C.nc"
) as ds:
    IMAGES = get_8bit_images(ds.images.data)

ROI_FILE = PARAMS.paths.examples / "roi.yaml"
