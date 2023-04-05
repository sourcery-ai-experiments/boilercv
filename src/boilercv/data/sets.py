"""Datasets."""

from collections.abc import Iterator

import xarray as xr

from boilercv.data import HEADER, ROI, VIDEO
from boilercv.data.packing import unpack
from boilercv.models.params import PARAMS
from boilercv.models.paths import LOCAL_PATHS, get_sorted_paths
from boilercv.types import DS

ALL_FRAMES = slice(None)
ALL_SOURCES = get_sorted_paths(PARAMS.paths.sources)
ALL_NAMES = [source.stem for source in ALL_SOURCES]


def get_all_datasets(
    num_frames: int = 0, frame: slice = ALL_FRAMES
) -> Iterator[tuple[DS, str]]:
    """Yield datasets in order."""
    for name in ALL_NAMES:
        yield get_dataset(name, num_frames, frame), name


def get_dataset(name: str, num_frames: int = 0, frame: slice = ALL_FRAMES) -> DS:
    """Load a video dataset."""
    # Can't use `xr.open_mfdataset` because it requires dask
    # Unpacking is incompatible with dask
    if num_frames:
        if frame == ALL_FRAMES:
            frame = slice(None, num_frames - 1)
        else:
            raise ValueError("Don't specify both `num_frames` and `frame`.")
    unc_source = LOCAL_PATHS.uncompressed_sources / f"{name}.nc"
    source = unc_source if unc_source.exists() else PARAMS.paths.sources / f"{name}.nc"
    roi = PARAMS.paths.rois / f"{name}.nc"
    with xr.open_dataset(source) as ds, xr.open_dataset(roi) as roi_ds:
        if not unc_source.exists():
            xr.Dataset({VIDEO: ds[VIDEO]}).to_netcdf(path=unc_source)
        return xr.Dataset(
            {
                VIDEO: unpack(ds[VIDEO].sel(frame=frame)),
                ROI: roi_ds[ROI],
                HEADER: ds[HEADER],
            }
        )


def get_large_dataset(video: str) -> DS:
    """Load a large video dataset."""
    with xr.open_dataset(LOCAL_PATHS.large_sources / f"{video}.nc") as ds:
        return ds
