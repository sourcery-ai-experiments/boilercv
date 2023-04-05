"""Get bubble contours."""

import cv2 as cv
import numpy as np
import pandas as pd
from loguru import logger

from boilercv.data import VIDEO
from boilercv.data.sets import ALL_NAMES, get_dataset
from boilercv.images import scale_bool
from boilercv.images.cv import find_contours
from boilercv.models.params import PARAMS
from boilercv.types import DF, Vid


def main():
    logger.info("start contours")
    destinations = [
        PARAMS.paths.contours / f"{video_name}.h5" for video_name in ALL_NAMES
    ]
    for source_name, destination in zip(ALL_NAMES, destinations, strict=True):
        if destination.exists():
            continue
        video = cv.bitwise_not(scale_bool(get_dataset(source_name)[VIDEO].values))
        df = get_all_contours(video, method=cv.CHAIN_APPROX_SIMPLE)
        df.to_hdf(
            destination,
            "contours",
            complib="zlib",
            complevel=9,
        )
    logger.info("finish contours")


def get_all_contours(video: Vid, method) -> DF:
    """Get all contours."""
    all_contours = np.vstack(
        [
            np.insert(
                np.vstack(
                    [
                        np.insert(contour, 0, cont_num, axis=1)
                        for cont_num, contour in enumerate(find_contours(image, method))
                    ]
                ),
                0,
                image_num,
                axis=1,
            )
            for image_num, image in enumerate(video)
        ]
    )
    return pd.DataFrame(
        all_contours, columns=["frame", "contour", "ypx", "xpx"]
    ).set_index(["frame", "contour"])


if __name__ == "__main__":
    main()
