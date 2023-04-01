"""Preview ROIs."""


import numpy as np
import xarray as xr

from boilercv.data import FRAME, ROI, VIDEO
from boilercv.gui import view_images
from boilercv.models.params import PARAMS
from boilercv.types import ImgLike


def main():
    preview: list[ImgLike] = []
    for source, roi in zip(
        sorted(PARAMS.paths.rois.iterdir()),
        sorted(PARAMS.paths.sources.iterdir()),
        strict=True,
    ):
        with xr.open_mfdataset([source, roi]) as ds:
            preview.extend(
                [
                    np.unpackbits(ds[VIDEO].isel({FRAME: 0}).values, axis=1),
                    ds[ROI].values,
                ]
            )
    view_images(preview)


if __name__ == "__main__":
    main()
