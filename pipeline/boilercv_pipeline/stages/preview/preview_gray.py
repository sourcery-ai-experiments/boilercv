"""Update previews for grayscale videos."""

from loguru import logger
from tqdm import tqdm

from boilercv.data import FRAME, VIDEO
from boilercv_pipeline.models.params import PARAMS
from boilercv_pipeline.sets import get_dataset
from boilercv_pipeline.stages.preview import new_videos_to_preview


def main():  # noqa: D103
    stage = "large_sources"
    destination = PARAMS.paths.gray_preview
    with new_videos_to_preview(destination) as videos_to_preview:
        for video_name in tqdm(videos_to_preview):
            if ds := get_dataset(video_name, stage=stage, num_frames=1):
                videos_to_preview[video_name] = ds[VIDEO].isel({FRAME: 0}).values


if __name__ == "__main__":
    logger.info("Start updating gray preview")
    main()
    logger.info("Finish updating gray preview")
