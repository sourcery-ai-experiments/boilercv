"""Binarize all videos and export their ROIs."""

import xarray as xr
from loguru import logger

from boilercv.data import FRAME, ROI, VIDEO, apply_to_img_da
from boilercv.data.packing import pack
from boilercv.images import scale_bool
from boilercv.images.cv import apply_mask, binarize, flood, get_roi
from boilercv.models.params import LOCAL_PATHS, PARAMS
from boilercv.models.paths import get_sorted_paths
from boilercv.types import DA


def main():
    logger.info("start binarize")
    for source in get_sorted_paths(LOCAL_PATHS.large_sources):
        destination = PARAMS.paths.sources / f"{source.stem}.nc"
        if destination.exists():
            continue
        with xr.open_dataset(source) as ds:
            video = ds[VIDEO]
            maximum = video.max(FRAME)
            flooded: DA = apply_to_img_da(flood, maximum)
            roi: DA = apply_to_img_da(get_roi, scale_bool(flooded))
            masked: DA = apply_to_img_da(
                apply_mask, video, scale_bool(roi), vectorize=True
            )
            binarized: DA = apply_to_img_da(binarize, masked, vectorize=True)
            ds[VIDEO] = pack(binarized)
            ds.to_netcdf(
                path=PARAMS.paths.sources / source.name,
                encoding={VIDEO: {"zlib": True}},
            )
            ds[ROI] = roi
            ds = ds.drop_vars(VIDEO)
            ds.to_netcdf(path=PARAMS.paths.rois / source.name)
    logger.info("finish binarize")


if __name__ == "__main__":
    main()
