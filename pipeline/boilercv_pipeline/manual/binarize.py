"""Binarize all videos and export their ROIs."""

from loguru import logger
from tqdm import tqdm
from xarray import open_dataset

from boilercv.data import FRAME, ROI, VIDEO, apply_to_img_da
from boilercv.data.packing import pack
from boilercv.images import scale_bool
from boilercv.images.cv import apply_mask, binarize, close_and_erode, flood
from boilercv.types import DA
from boilercv_pipeline.models.params import PARAMS
from boilercv_pipeline.models.paths import get_sorted_paths


def main():  # noqa: D103
    logger.info("start binarize")
    for source in tqdm(get_sorted_paths(PARAMS.paths.large_sources)):
        destination = PARAMS.paths.sources / f"{source.stem}.nc"
        if destination.exists():
            continue
        with open_dataset(source) as ds:
            video = ds[VIDEO]
            maximum = video.max(FRAME)
            flooded: DA = apply_to_img_da(flood, maximum)
            roi: DA = apply_to_img_da(close_and_erode, scale_bool(flooded))
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
