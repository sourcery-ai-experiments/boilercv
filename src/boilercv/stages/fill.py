"""Fill bubble contours."""

import cv2 as cv
import numpy as np
import xarray as xr
from loguru import logger

from boilercv.data import ROI, VIDEO
from boilercv.data.frames import idx
from boilercv.data.packing import pack
from boilercv.data.sets import get_all_datasets, get_contours_df
from boilercv.images.cv import draw_contours
from boilercv.models.params import PARAMS
from boilercv.types import ArrInt


def main():
    for ds, name in get_all_datasets():
        destination = PARAMS.paths.filled / f"{name}.nc"
        if destination.exists():
            continue

        df = get_contours_df(name)
        ds = xr.zeros_like(ds, dtype=np.uint8)
        video = ds[VIDEO]
        if not df.empty:
            for frame_num, frame in enumerate(video):
                try:
                    video[frame_num, :, :] = loop(df, frame_num, frame)
                except Exception:
                    logger.exception("Failed to fill contours")
        ds[VIDEO] = pack(video)
        ds = ds.drop_vars(ROI)
        ds.to_netcdf(path=destination)


def loop(df, frame_num, frame):
    contours: list[ArrInt] = list(  # type: ignore
        df.loc[idx[frame_num], :]  # type: ignore
        .groupby("contour")
        .apply(lambda grp: grp.values)  # type: ignore
    )
    return draw_contours(frame.values, contours, thickness=cv.FILLED)


if __name__ == "__main__":
    logger.info("start fill contours")
    main()
    logger.info("finish fill contours")
