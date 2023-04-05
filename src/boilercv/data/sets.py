"""Datasets."""

from collections.abc import Iterator

import xarray as xr

from boilercv.data import HEADER, ROI, VIDEO
from boilercv.data.packing import unpack
from boilercv.models.params import PARAMS
from boilercv.models.paths import iter_sorted
from boilercv.types import DS

ALL_FRAMES = slice(None)


def get_all_datasets(
    num_frames: int = 0, frame: slice = ALL_FRAMES
) -> Iterator[tuple[DS, str]]:
    """Yield datasets in order."""
    videos = [source.stem for source in iter_sorted(PARAMS.paths.sources)]
    for video in videos:
        yield get_dataset(video, num_frames, frame), video


def get_dataset(video: str, num_frames: int = 0, frame: slice = ALL_FRAMES) -> DS:
    """Load a video dataset."""
    # Can't use `xr.open_mfdataset` because it requires dask
    # Downstream computations (e.g. unpack) are incompatible with dask
    source = PARAMS.paths.sources / f"{video}.nc"
    roi = PARAMS.paths.rois / f"{video}.nc"
    if num_frames and frame == ALL_FRAMES:
        frame = slice(None, num_frames - 1)
    with xr.open_dataset(source) as ds, xr.open_dataset(roi) as roi_ds:
        return xr.Dataset(
            {
                VIDEO: unpack(ds[VIDEO].sel(frame=frame)),
                ROI: roi_ds[ROI],
                HEADER: ds[HEADER],
            }
        )


def get_large_dataset(video: str) -> DS:
    """Load a large video dataset."""
    with xr.open_dataset(PARAMS.paths.large_sources / f"{video}.nc") as ds:
        return ds
