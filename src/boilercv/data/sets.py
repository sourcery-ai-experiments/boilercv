"""Datasets."""

from collections.abc import Iterator

import pandas as pd
import xarray as xr

from boilercv.data import DIMS, HEADER, ROI, VIDEO
from boilercv.data.packing import unpack
from boilercv.models.params import PARAMS
from boilercv.models.paths import LOCAL_PATHS, get_sorted_paths
from boilercv.types import DF, DS

ALL_FRAMES = slice(None)
ALL_SOURCES = get_sorted_paths(PARAMS.paths.sources)
ALL_NAMES = [source.stem for source in ALL_SOURCES]


def get_shape(ds: DS) -> tuple[int, int, int]:
    """Get the shape of the video."""
    shape_keys = [f"source_{dim}" for dim in DIMS]
    return tuple(ds.attrs[key] for key in shape_keys)


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
    frame = slice_frames(num_frames, frame)
    unc_source = LOCAL_PATHS.uncompressed_sources / f"{name}.nc"
    source = unc_source if unc_source.exists() else PARAMS.paths.sources / f"{name}.nc"
    roi = PARAMS.paths.rois / f"{name}.nc"
    with xr.open_dataset(source) as ds, xr.open_dataset(roi) as roi_ds:
        if not unc_source.exists():
            xr.Dataset({VIDEO: ds[VIDEO], HEADER: ds[HEADER]}).to_netcdf(
                path=unc_source
            )
        return xr.Dataset(
            {
                VIDEO: unpack(ds[VIDEO].sel(frame=frame)),
                ROI: roi_ds[ROI],
                HEADER: ds[HEADER],
            },
            attrs={f"source_{dim}": length for dim, length in ds.dims.items()},
        )


def get_large_dataset(name: str) -> DS:
    """Load a large video dataset."""
    with xr.open_dataset(LOCAL_PATHS.large_sources / f"{name}.nc") as ds:
        return ds


def get_contours_df(name: str) -> DF:
    """Load contours from a dataset."""
    unc_cont = LOCAL_PATHS.uncompressed_contours / f"{name}.h5"
    contour = unc_cont if unc_cont.exists() else PARAMS.paths.contours / f"{name}.h5"
    contour_df: DF = pd.read_hdf(contour)  # type: ignore
    if not unc_cont.exists():
        contour_df.to_hdf(unc_cont, key="contours", complevel=None, complib=None)
    return contour_df


def slice_frames(num_frames: int, frame: slice) -> slice:
    """Returns a slice suitable for getting frames from datasets."""
    if num_frames:
        if frame == ALL_FRAMES:
            frame = slice(None, num_frames - 1)
        else:
            raise ValueError("Don't specify both `num_frames` and `frame`.")
    return frame
