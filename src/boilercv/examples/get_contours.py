"""Get bubble contours."""

import cv2 as cv
import numpy as np
import pandas as pd

from boilercv import DEBUG
from boilercv.data import VIDEO
from boilercv.data.frames import idx
from boilercv.data.sets import get_dataset
from boilercv.examples import EXAMPLE_VIDEO_NAME
from boilercv.gui import view_images
from boilercv.images import scale_bool
from boilercv.images.cv import draw_contours, find_contours
from boilercv.models.params import PARAMS
from boilercv.types import DF, Vid

NUM_FRAMES = 1000


def main():
    ds = get_dataset(EXAMPLE_VIDEO_NAME, NUM_FRAMES)
    video = ds[VIDEO]
    df = get_all_contours(scale_bool(~video.values), method=cv.CHAIN_APPROX_SIMPLE)
    df.to_hdf(PARAMS.paths.examples / f"{EXAMPLE_VIDEO_NAME}.h5", "contours")
    if DEBUG:
        result = [
            draw_contours(scale_bool(frame.values), df.loc[idx[i, :, :], :].values)
            for i, frame in enumerate(video)
        ]
        view_images(result)


def get_all_contours(video: Vid, method: int = cv.CHAIN_APPROX_NONE) -> DF:
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
