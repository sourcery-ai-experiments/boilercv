"""Fill bubble contours."""

import cv2 as cv
import numpy as np
import pandas as pd
import xarray as xr
from loguru import logger

from boilercv import PREVIEW
from boilercv.captivate.previews import view_images
from boilercv.data import IDX, ROI, VIDEO
from boilercv.data.packing import pack, unpack
from boilercv.data.sets import get_contours_df, get_dataset
from boilercv.examples import EXAMPLE_NUM_FRAMES, EXAMPLE_VIDEO_NAME
from boilercv.images.cv import draw_contours
from boilercv.models.params import PARAMS
from boilercv.types import ArrInt

TRY_EMPTY = False


def main():
    if TRY_EMPTY:
        all_contours = np.empty((0, 4))
        df = pd.DataFrame(
            all_contours, columns=["frame", "contour", "ypx", "xpx"]
        ).set_index(["frame", "contour"])
    else:
        df = get_contours_df(EXAMPLE_VIDEO_NAME)
    ds = xr.zeros_like(
        get_dataset(EXAMPLE_VIDEO_NAME, EXAMPLE_NUM_FRAMES), dtype=np.uint8
    )
    video = ds[VIDEO]
    if not df.empty:
        for frame_num, frame in enumerate(video):
            contours: list[ArrInt] = list(  # type: ignore
                df.loc[IDX[frame_num], :]  # type: ignore
                .groupby("contour")
                .apply(lambda grp: grp.values)  # type: ignore
            )
            video[frame_num, :, :] = draw_contours(
                frame.values, contours, thickness=cv.FILLED
            )
    ds[VIDEO] = pack(video)
    ds = ds.drop_vars(ROI)
    destination = PARAMS.paths.examples / f"{EXAMPLE_VIDEO_NAME}_filled.nc"
    ds.to_netcdf(path=destination)
    if PREVIEW:
        with xr.open_dataset(destination) as ds2:
            view_images([unpack(ds[VIDEO]), unpack(ds2[VIDEO])])


if __name__ == "__main__":
    logger.info("start fill contours")
    main()
    logger.info("finish fill contours")
