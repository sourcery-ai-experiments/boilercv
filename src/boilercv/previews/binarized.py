"""Preview the binarization stage."""

import xarray as xr

from boilercv.data import VIDEO, VIDEO_NAME, YX_PX, identity_da
from boilercv.gui import view_images
from boilercv.images import draw_text, scale_bool
from boilercv.models.params import PARAMS
from boilercv.types import DA


def main():
    with xr.open_dataset(PARAMS.paths.binarized_preview) as ds:
        da = draw_text_da(ds[VIDEO])
        view_images(da)


def draw_text_da(da: DA) -> DA:
    """Draw text on images in a data array.

    Args:
        da: Data array.
    """
    return xr.apply_ufunc(
        draw_text,
        scale_bool(da),
        identity_da(da, VIDEO_NAME),
        input_core_dims=(YX_PX, []),
        output_core_dims=(YX_PX,),
        vectorize=True,
    )


if __name__ == "__main__":
    main()
