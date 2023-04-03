"""Binarize all videos and export their ROIs."""

import xarray as xr
from loguru import logger

from boilercv.data import FRAME, ROI, VIDEO, apply_to_img_da
from boilercv.data.packing import pack
from boilercv.images import scale_bool
from boilercv.images.cv import apply_mask, binarize, flood, morph
from boilercv.models.params import PARAMS
from boilercv.models.paths import iter_sorted
from boilercv.types import DA


def main():
    sources = iter_sorted(PARAMS.paths.large_sources)
    for source in sources:
        try:
            loop(source)
        except Exception:
            logger.exception(source.stem)
            continue


def loop(source):
    with xr.open_dataset(source) as ds:
        video = ds[VIDEO]
        maximum = video.max(FRAME)
        flooded: DA = apply_to_img_da(flood, maximum)
        _, roi, _ = apply_to_img_da(morph, scale_bool(flooded), returns=3)
        masked: DA = apply_to_img_da(apply_mask, video, scale_bool(roi), vectorize=True)
        binarized: DA = apply_to_img_da(binarize, masked, vectorize=True)
        ds[VIDEO] = pack(binarized)
        ds.to_netcdf(
            path=PARAMS.paths.sources / source.name,
            encoding={VIDEO: {"zlib": True}},
        )
        ds[ROI] = roi
        ds = ds.drop_vars(VIDEO)
        ds.to_netcdf(path=PARAMS.paths.rois / source.name)


if __name__ == "__main__":
    main()
