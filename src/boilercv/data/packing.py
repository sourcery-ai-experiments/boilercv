"""Packing and unpacking of binarized video data."""

import numpy as np
import xarray as xr

from boilercv.data import (
    DIMS,
    PACKED,
    PACKED_DIM_INDEX,
    PACKED_DIMS,
    VIDEO,
    XPX,
    XPX_PACKED,
)
from boilercv.types import DA


def pack(da: DA) -> DA:
    """Pack the bits in dimension of the data array."""
    return (
        xr.apply_ufunc(
            np.packbits,
            da,
            kwargs=dict(axis=PACKED_DIM_INDEX),
            input_core_dims=[DIMS],
            output_core_dims=[DIMS],
            exclude_dims={XPX},
            keep_attrs=True,
        )
        .rename({XPX: XPX_PACKED})
        .rename(f"{VIDEO}_{PACKED}")
    )


def unpack(da: DA) -> DA:
    """Unpack the bits of the last image dimension of a data array."""
    return (
        xr.apply_ufunc(
            np.unpackbits,
            da,
            kwargs=dict(axis=PACKED_DIM_INDEX),
            input_core_dims=[PACKED_DIMS],
            output_core_dims=[PACKED_DIMS],
            exclude_dims={XPX_PACKED},
            keep_attrs=True,
        )
        .rename({XPX_PACKED: XPX})
        .rename(VIDEO)
        .astype(bool)
    )
