"""Update previews for the filled contours stage."""

from loguru import logger

from boilercv.data import FRAME, VIDEO, VIDEO_NAME, assign_ds
from boilercv.data.models import Dimension
from boilercv.data.sets import get_all_datasets
from boilercv.data.video import XPX_DIM, YPX_DIM
from boilercv.gui import MultipleViewable, pad_images
from boilercv.models.params import PARAMS


def main():
    preview: MultipleViewable = []
    video_names: list[str] = []
    for ds, video_name in get_all_datasets(num_frames=1, stage="filled"):
        first_frame = ds[VIDEO].isel({FRAME: 0}).values
        preview.append(first_frame)
        video_names.append(video_name)
    preview = pad_images(preview)
    ds = assign_ds(
        name=VIDEO,
        long_name="Video preview",
        units="Pixel state",
        dims=(
            Dimension(
                dim=VIDEO_NAME,
                long_name="Video name",
                coords=video_names,
            ),
            YPX_DIM,
            XPX_DIM,
        ),
        data=preview,
    )
    ds.to_netcdf(path=PARAMS.paths.filled_preview)


if __name__ == "__main__":
    logger.info("Start update filled preview")
    main()
    logger.info("Finish update filled preview")
