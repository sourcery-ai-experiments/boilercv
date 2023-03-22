"""Example of converting CINE files to the NetCDF file format."""

from dataclasses import asdict

import numpy as np
import xarray as xr
from scipy.spatial.distance import euclidean

from boilercv import SAMPLE_DIAMETER_UM, TIMEZONE, get_8bit_images
from boilercv.gui import get_video_images
from boilercv.images import load_roi
from boilercv.models.params import PARAMS
from boilercv.types import ArrIntDef
from boilercv.video.cine import get_cine_attributes


def main():
    images_name = "images"
    source = PARAMS.paths.examples / "results_2022-11-30T12-39-07_98C.cine"
    destination = PARAMS.paths.examples / f"{source.stem}.nc"
    length_units = "um"

    header, utc = get_cine_attributes(source, TIMEZONE)
    elapsed = utc - utc[0]
    images = xr.DataArray(
        name=images_name,
        dims=("time", "y", "x"),
        coords=dict(time=elapsed, utc=("time", utc)),
        data=list(get_8bit_images(get_video_images(source))),
        attrs=asdict(header)
        | dict(long_name="High-speed video data", units="intensity"),
    )
    images["time"] = images.time.assign_attrs(dict(long_name="Time elapsed"))
    images["utc"] = images.utc.assign_attrs(dict(long_name="UTC time"))

    roi = load_roi(images.data, PARAMS.paths.examples / "roi_line.yaml", "line")
    px_per_um = euclidean(*iter(roi)) / SAMPLE_DIAMETER_UM

    def scale(coord: ArrIntDef) -> ArrIntDef:
        """Scale coordinates to nanometers."""
        return np.round(coord / px_per_um).astype(int)

    images = images.assign_coords(dict(y=scale(images.y), x=scale(images.x)))

    images["y"] = images.y.assign_attrs(dict(long_name="Height", units=length_units))
    images["x"] = images.x.assign_attrs(dict(long_name="Width", units=length_units))

    xr.Dataset(coords={images_name: images}).to_netcdf(path=destination)


if __name__ == "__main__":
    main()
