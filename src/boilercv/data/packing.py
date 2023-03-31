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
from boilercv.types import DS


def pack(ds: DS) -> DS:
    """Pack the bits in dimension of the data array."""
    packed = (
        xr.apply_ufunc(
            np.packbits,
            ds[VIDEO],
            kwargs=dict(axis=PACKED_DIM_INDEX),
            input_core_dims=[DIMS],
            output_core_dims=[DIMS],
            exclude_dims={XPX},
            keep_attrs=True,
        )
        .rename({XPX: XPX_PACKED})
        .rename(f"{VIDEO}_{PACKED}")
    )
    ds[VIDEO] = packed
    return ds


def unpack(ds: DS) -> DS:
    """Unpack the bits of the last image dimension of a data array."""
    unpacked = (
        xr.apply_ufunc(
            np.unpackbits,
            ds[VIDEO],
            kwargs=dict(axis=PACKED_DIM_INDEX),
            input_core_dims=[PACKED_DIMS],
            output_core_dims=[PACKED_DIMS],
            exclude_dims={XPX_PACKED},
            keep_attrs=True,
        )
        .rename({XPX_PACKED: XPX})
        .rename(VIDEO)
    ).astype(bool)
    ds[VIDEO] = unpacked
    return ds
