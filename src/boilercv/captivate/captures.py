"""Image and video capturing."""

from pathlib import Path

import imageio
import numpy as np
from loguru import logger

from boilercv import FFMPEG_LOG_LEVEL, FRAMERATE_CONT
from boilercv.images import scale_bool
from boilercv.types import DA, Img, ImgBool, Vid, VidBool


def write_video(
    path: Path,
    video: Vid | VidBool | DA,
    framerate: int = FRAMERATE_CONT,
    preview_frame: bool = False,
):
    """Write a video to disk with the default filetype and timestamp.

    Args:
        path: Path to the video file (suffix coerced to '.mp4').
        video: Data structure to write as a video.
        framerate: Frames per second. Default: Package default framerate.
        preview_frame: Write the first frame to disk as an image. Default: False.
    """
    video = coerce_input(video)
    if path.suffix and path.suffix != ".mp4":
        logger.warning(f"Changing extesion of {path}  to '.mp4'.")
    path = path.with_suffix(".mp4")
    writer = imageio.get_writer(
        uri=path, fps=framerate, macro_block_size=8, ffmpeg_log_level=FFMPEG_LOG_LEVEL
    )
    for image in video:
        writer.append_data(image)
    writer.close()
    if preview_frame:
        write_image(path.with_suffix(".png"), video[0])


def write_image(path: Path, image: Img | ImgBool | DA):
    """Write an image to disk with default filetype.

    Args:
        path: Path to the image file (suffix coerced to '.png').
        image: Data structure to write as an image.
    """
    image = coerce_input(image)
    if path.suffix and path.suffix != ".png":
        logger.warning(f"Changing extesion of {path} to '.png'.")
    path = path.with_suffix(".png")
    imageio.imwrite(path, image)


def coerce_input(imgs: Img | ImgBool | DA) -> Img:
    """Coerce input image or video to the appropriate type.

    Args:
        imgs: Image or video to coerce.
    """
    if np.issubdtype(imgs.dtype, np.integer):
        viewable: Img = imgs.values if isinstance(imgs, DA) else imgs  # type: ignore
    elif np.issubdtype(imgs.dtype, bool):
        viewable: Img = (
            scale_bool(imgs.values) if isinstance(imgs, DA) else scale_bool(imgs)
        )
    else:
        raise TypeError(f"Cannot coerce {type(imgs)} to a viewable type.")
    return viewable
