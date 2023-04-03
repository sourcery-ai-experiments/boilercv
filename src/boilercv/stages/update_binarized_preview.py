"""Update previews for the binarization stage."""

import numpy as np

from boilercv import DEBUG
from boilercv.data import FRAME, ROI, VIDEO, assign_ds, img_datasets
from boilercv.data.models import Dimension
from boilercv.data.video import XPX_DIM, YPX_DIM
from boilercv.gui import MultipleViewable, pad_images, view_images
from boilercv.models.params import PARAMS


def main():
    preview: MultipleViewable = []
    video_names: list[str] = []
    for ds, video_name in img_datasets():
        vid = np.unpackbits(ds[VIDEO].isel({FRAME: 0}).values, axis=1)
        preview.append(vid & ds[ROI].values)
        video_names.append(video_name)
    preview = pad_images(preview)
    video_name_dim = Dimension(
        dim="video_name",
        long_name="Video name",
        coords=video_names,
    )
    ds = assign_ds(
        name=VIDEO,
        long_name="Video preview",
        units="Pixel state",
        dims=(video_name_dim, YPX_DIM, XPX_DIM),
        data=preview,
    )
    ds.to_netcdf(path=PARAMS.paths.binarized_preview)
    if DEBUG:
        view_images(ds, play_rate=2)


if __name__ == "__main__":
    main()
