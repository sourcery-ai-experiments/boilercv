"""Preview results."""

import xarray as xr

from boilercv.data import VIDEO_NAME, YX_PX, identity_da
from boilercv.images import draw_text, overlay
from boilercv.types import DA


def draw_text_da(da: DA) -> DA:
    """Draw text on images in a data array.

    Args:
        da: Data array.
    """
    if da.ndim == 4:
        # We have a color video
        return xr.apply_ufunc(
            draw_text,
            da,
            identity_da(da, VIDEO_NAME),
            input_core_dims=([*YX_PX, "channel"], []),
            output_core_dims=([*YX_PX, "channel"],),
            vectorize=True,
        )
    else:
        return xr.apply_ufunc(
            draw_text,
            da,
            identity_da(da, VIDEO_NAME),
            input_core_dims=(YX_PX, []),
            output_core_dims=(YX_PX,),
            vectorize=True,
        )


def overlay_da(da_image: DA, da_overlay: DA) -> DA:
    """Draw text on images in a data array.

    Args:
        da_image: Image data array.
        da_overlay: Overlay data array.
    """
    return xr.apply_ufunc(
        overlay,
        da_image,
        da_overlay,
        input_core_dims=(YX_PX, YX_PX),
        output_core_dims=([*YX_PX, "channel"],),
        vectorize=True,
    )
