"""Image and video capturing."""

from datetime import datetime
from pathlib import Path

import imageio
from loguru import logger

from boilercv import FFMPEG_LOG_LEVEL, FRAMERATE_CONT
from boilercv.images import scale_bool
from boilercv.types import DA, Img, ImgBool, Vid, VidBool


def write_video(
    path: Path,
    video: Vid | VidBool | DA,
    timestamp: str | None = None,
    framerate: int = FRAMERATE_CONT,
    preview_frame: bool = False,
):
    """Write a video to disk with the default filetype and timestamp.

    Args:
        path: Path to the video file (suffix coerced to '.mp4').
        video: Data structure to write as a video.
        timestamp: Custom timestamp for the file. Default: The current time.
        framerate: Frames per second. Default: Package default framerate.
        preview_frame: Write the first frame to disk as an image. Default: False.
    """
    video = coerce_input(video)
    timestamp = timestamp or get_timestamp()
    if path.suffix and path.suffix != ".mp4":
        logger.warning(f"Changing extesion of {path}  to '.mp4'.")
    path = path.with_name(f"{path.stem}_{timestamp}").with_suffix(".mp4")
    writer = imageio.get_writer(
        uri=path, fps=framerate, macro_block_size=8, ffmpeg_log_level=FFMPEG_LOG_LEVEL
    )
    for image in video:
        writer.append_data(image)
    writer.close()
    if preview_frame:
        write_image(path.with_suffix(".png"), video[0])


def write_image(path: Path, image: Img | ImgBool | DA, timestamp: str | None = None):
    """Write an image to disk with default filetype and timestamp.

    Args:
        path: Path to the image file (suffix coerced to '.png').
        image: Data structure to write as an image.
        timestamp: Custom timestamp for the file. Default: The current time.
    """
    image = coerce_input(image)
    timestamp = timestamp or get_timestamp()
    if path.suffix and path.suffix != ".png":
        logger.warning(f"Changing extesion of {path} to '.png'.")
    path = path.with_name(f"{path.stem}_{timestamp}").with_suffix(".png")
    imageio.imwrite(path, image)


def coerce_input(img_or_vid: Img | ImgBool | DA) -> Img:
    """Coerce input image or video to the appropriate type.

    Args:
        img_or_vid: Image or video to coerce.
    """
    if img_or_vid.dtype == bool:
        viewable: Img = scale_bool(img_or_vid)
    if isinstance(img_or_vid, DA):
        viewable: Img = img_or_vid.values
    else:
        raise TypeError(f"Cannot coerce {type(img_or_vid)} to a viewable type.")
    return viewable


def get_timestamp():
    """Produce a timestamp suitable for filenames.

    Truncate microseconds and replace colons with dashes in an ISO 8601 time string."""
    return datetime.now().replace(microsecond=0).isoformat().replace(":", "-")
