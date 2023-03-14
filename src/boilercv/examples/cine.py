"""Example of finding ROI in a CINE file."""

import sys

import numpy as np
from loguru import logger
from pycine.raw import read_frames

from boilercv.examples import interact_with_video
from boilercv.models.params import Params


def main():
    logger.add(sink=sys.stderr, level="TRACE")
    images, *_ = read_frames(
        cine_file=Params.get_params().paths.examples_data
        / "results_2022-11-30T12-39-07_98C.cine"
    )
    video = np.stack(list(images))
    interact_with_video(video)


if __name__ == "__main__":
    main()
