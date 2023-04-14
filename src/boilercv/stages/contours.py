"""Get bubble contours."""

import cv2 as cv
import numpy as np
import pandas as pd
from loguru import logger

from boilercv.data import VIDEO
from boilercv.data.sets import get_dataset, get_unprocessed_destinations
from boilercv.images import scale_bool
from boilercv.images.cv import find_contours
from boilercv.models.params import PARAMS
from boilercv.types import DF, Vid


def main():
    destinations = get_unprocessed_destinations(PARAMS.paths.contours, ext="h5")
    for source_name, destination in destinations.items():
        video = cv.bitwise_not(scale_bool(get_dataset(source_name)[VIDEO].values))
        df = get_all_contours(video, method=cv.CHAIN_APPROX_SIMPLE)
        df.to_hdf(
            destination,
            "contours",
            complib="zlib",
            complevel=9,
        )


def get_all_contours(video: Vid, method) -> DF:
    """Get all contours."""
    try:
        all_contours = np.vstack(
            [
                np.insert(
                    np.vstack(
                        [
                            np.insert(contour, 0, cont_num, axis=1)
                            for cont_num, contour in enumerate(
                                find_contours(image, method)
                            )
                        ]
                    ),
                    0,
                    image_num,
                    axis=1,
                )
                for image_num, image in enumerate(video)
            ]
        )
    except ValueError:
        logger.exception("no contours found")
        all_contours = np.empty((0, 4))
    return pd.DataFrame(
        all_contours, columns=["frame", "contour", "ypx", "xpx"]
    ).set_index(["frame", "contour"])


if __name__ == "__main__":
    logger.info("start finding contours")
    main()
    logger.info("finish finding contours")
