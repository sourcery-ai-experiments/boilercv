"""Fill bubble contours."""

import cv2 as cv
import xarray as xr
from loguru import logger

from boilercv.data import ROI, VIDEO
from boilercv.data.packing import pack
from boilercv.data.sets import get_contours_df, get_dataset, process_datasets
from boilercv.images.cv import draw_contours
from boilercv.models.params import PARAMS
from boilercv.types import ArrInt


def main():
    destination = PARAMS.paths.filled
    with process_datasets(destination) as videos_to_process:
        for name in videos_to_process:
            df = get_contours_df(name)
            source_ds = get_dataset(name)
            ds = xr.zeros_like(source_ds, dtype=source_ds[VIDEO].dtype)
            video = ds[VIDEO]
            if not df.empty:
                for frame_num, frame in enumerate(video):
                    contours: list[ArrInt] = list(
                        df.loc[frame_num, :]
                        .groupby("contour")
                        .apply(lambda grp: grp.values)
                    )
                    video[frame_num, :, :] = draw_contours(
                        frame.values, contours, thickness=cv.FILLED
                    )
            ds[VIDEO] = pack(video)
            ds = ds.drop_vars(ROI)
            videos_to_process[name] = ds


if __name__ == "__main__":
    logger.info("start fill contours")
    main()
    logger.info("finish fill contours")
