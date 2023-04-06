"""Preview results."""


import xarray as xr

from boilercv.data import VIDEO_NAME, YX_PX, identity_da
from boilercv.images import draw_text, scale_bool
from boilercv.types import DA


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
