"""Datasets."""

from collections.abc import Iterator
from pathlib import Path
from typing import Literal, TypeAlias

import pandas as pd
import xarray as xr

from boilercv.data import HEADER, ROI, VIDEO
from boilercv.data.packing import unpack
from boilercv.models.params import LOCAL_PATHS, PARAMS
from boilercv.models.paths import get_sorted_paths
from boilercv.types import DF, DS

ALL_FRAMES = slice(None)
ALL_SOURCES = get_sorted_paths(PARAMS.paths.sources)
ALL_NAMES = [source.stem for source in ALL_SOURCES]

Stage: TypeAlias = Literal["large_sources", "sources", "filled"]
STAGE_DEFAULT = "sources"


def get_all_datasets(
    num_frames: int = 0, frame: slice = ALL_FRAMES, stage: Stage = STAGE_DEFAULT
) -> Iterator[tuple[DS, str]]:
    """Yield datasets in order."""
    for name in ALL_NAMES:
        yield get_dataset(name, num_frames, frame, stage), name


def inspect_dataset(name: str, stage: Stage = STAGE_DEFAULT) -> DS:
    """Inspect a video dataset."""
    cmp_source, unc_source = get_stage(name, stage)
    source = unc_source if unc_source.exists() else cmp_source
    if stage == "large_sources":
        return xr.open_dataset(source) if source.exists() else xr.Dataset()
    with xr.open_dataset(source) as ds:
        return ds


def get_dataset(
    name: str,
    num_frames: int = 0,
    frame: slice = ALL_FRAMES,
    stage: Stage = STAGE_DEFAULT,
) -> DS:
    """Load a video dataset."""
    # Can't use `xr.open_mfdataset` because it requires dask
    # Unpacking is incompatible with dask
    frame = slice_frames(num_frames, frame)
    cmp_source, unc_source = get_stage(name, stage)
    source = unc_source if unc_source.exists() else cmp_source
    if stage == "large_sources":
        ds = xr.open_dataset(source)
        return (
            xr.Dataset({VIDEO: ds[VIDEO].sel(frame=frame), HEADER: ds[HEADER]})
            if source.exists()
            else xr.Dataset()
        )
    roi = PARAMS.paths.rois / f"{name}.nc"
    with xr.open_dataset(source) as ds, xr.open_dataset(roi) as roi_ds:
        if not unc_source.exists():
            xr.Dataset({VIDEO: ds[VIDEO], HEADER: ds[HEADER]}).to_netcdf(
                path=unc_source, encoding={VIDEO: {"zlib": False}}
            )
        return xr.Dataset(
            {
                VIDEO: unpack(ds[VIDEO].sel(frame=frame)),
                ROI: roi_ds[ROI],
                HEADER: ds[HEADER],
            }
        )


def get_stage(name: str, stage: Stage = STAGE_DEFAULT) -> tuple[Path, Path]:
    """Get the paths associated with a particular video name and pipeline stage."""
    if stage == "sources":
        unc_source = LOCAL_PATHS.uncompressed_sources / f"{name}.nc"
        return PARAMS.paths.sources / f"{name}.nc", unc_source
    elif stage == "large_sources":
        source = unc_source = LOCAL_PATHS.large_sources / f"{name}.nc"
        return source, unc_source
    elif stage == "filled":
        unc_source = LOCAL_PATHS.uncompressed_filled / f"{name}.nc"
        return PARAMS.paths.filled / f"{name}.nc", unc_source
    else:
        raise ValueError(f"Unknown stage: {stage}")


def get_contours_df(name: str) -> DF:
    """Load contours from a dataset."""
    unc_cont = LOCAL_PATHS.uncompressed_contours / f"{name}.h5"
    contour = unc_cont if unc_cont.exists() else PARAMS.paths.contours / f"{name}.h5"
    contour_df: DF = pd.read_hdf(contour)  # type: ignore
    if not unc_cont.exists():
        contour_df.to_hdf(unc_cont, key="contours", complevel=None, complib=None)
    return contour_df


def slice_frames(num_frames: int = 0, frame: slice = ALL_FRAMES) -> slice:
    """Returns a slice suitable for getting frames from datasets."""
    if num_frames:
        if frame == ALL_FRAMES:
            frame = slice(None, num_frames - 1)
        else:
            raise ValueError("Don't specify both `num_frames` and `frame`.")
    return frame
