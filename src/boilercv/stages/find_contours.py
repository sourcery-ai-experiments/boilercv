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
        df.to_hdf(destination, "contours", complib="zlib", complevel=9)


def get_all_contours(video: Vid, method) -> DF:
    """Get all contours in a video.

    Produces a dataframe with a multi-index of the video frame and contour number, and
    two columns indicating the "y" and "x" pixel locations of contour vertices.

    Args:
        video: Video to get contours from.
        method: The contour approximation method to use.
    """
    # This nested, pure-numpy approach is a bit hard to follow, but it is much faster
    # than the more readable approach of building and concatenating dataframes. The
    # overhead of dataframe creation over ~6000 frames is significant.
    try:
        # Vertically stack the contours detected in each frame
        all_contours = np.vstack(
            # For each frame in the video...
            [
                # Compose two columns, the frame number and the contours
                np.insert(
                    axis=1,  # Insert column-wise
                    obj=0,  # Insert at the beginning, e.g. prepend
                    values=frame_num,
                    # Vertically stack the pixel locations of each contour
                    arr=np.vstack(
                        # For each contour in the frame...
                        [
                            # Prepend the contour number to the contour locations
                            np.insert(axis=1, obj=0, values=cont_num, arr=contour)
                            for cont_num, contour in enumerate(
                                find_contours(image, method)
                            )
                        ]
                    ),
                )
                for frame_num, image in enumerate(video)
            ]
        )
    except ValueError:
        # Some frames may have no contours. Signal this with an empty array
        logger.warning("No contours found in this frame.")
        all_contours = np.empty((0, 4))
    # Build the dataframe at the very end to avoid the overhead
    return pd.DataFrame(
        all_contours, columns=["frame", "contour", "ypx", "xpx"]
    ).set_index(["frame", "contour"])


if __name__ == "__main__":
    logger.info("Start finding contours")
    main()
    logger.info("Finish finding contours")
