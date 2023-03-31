"""Binarize all videos in NetCDF."""

import xarray as xr

from boilercv.data import FRAME, VIDEO, apply_to_img_da
from boilercv.data.packing import pack
from boilercv.images import scale_bool
from boilercv.images.cv import apply_mask, binarize, flood, morph
from boilercv.models.params import PARAMS
from boilercv.types import DA


def main():
    sources = sorted(PARAMS.paths.large_sources.glob("*.nc"))
    for source in sources:
        destination = PARAMS.paths.sources / source.name
        with xr.open_dataset(source) as ds:
            video = ds[VIDEO]
            maximum = video.max(FRAME)
            flooded: DA = apply_to_img_da(flood, maximum)
            _, roi, _ = apply_to_img_da(morph, scale_bool(flooded), returns=3)
            masked: DA = apply_to_img_da(
                apply_mask, video, scale_bool(roi), vectorize=True
            )
            binarized: DA = apply_to_img_da(binarize, masked, vectorize=True)
            ds[VIDEO] = pack(binarized)
            ds.to_netcdf(path=destination, encoding={VIDEO: {"zlib": True}})


if __name__ == "__main__":
    main()
