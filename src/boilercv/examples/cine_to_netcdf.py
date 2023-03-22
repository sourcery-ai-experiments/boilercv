"""Example of converting CINE files to the NetCDF file format."""

import numpy as np
import xarray as xr
from scipy.spatial.distance import euclidean

from boilercv import TIMEZONE, get_8bit_images
from boilercv.gui import get_video_images
from boilercv.images import load_roi
from boilercv.models.params import PARAMS
from boilercv.types import ArrIntDef
from boilercv.video.cine import get_cine_attributes


def main():
    source = PARAMS.paths.examples / "results_2022-11-30T12-39-07_98C.cine"
    destination = PARAMS.paths.examples / f"{source.stem}.nc"
    images = list(get_8bit_images(get_video_images(source)))
    attrs, utc = get_cine_attributes(source, TIMEZONE)
    elapsed = utc - utc[0]
    images = xr.DataArray(
        name="images",
        dims=("time", "y", "x"),
        coords=dict(time=elapsed, utc=("time", utc)),
        data=list(get_8bit_images(get_video_images(source))),
        attrs=attrs | dict(long_name="High-speed video data", units="intensity"),
    )
    images["time"] = images.time.assign_attrs(dict(long_name="Time elapsed"))
    images["utc"] = images.utc.assign_attrs(dict(long_name="UTC time"))
    roi_file = PARAMS.paths.examples / "roi_line.yaml"
    roi = load_roi(images.data, roi_file, "line")
    px_per_nm = euclidean(*iter(roi)) / 9_525_000

    def scale(coord: ArrIntDef) -> ArrIntDef:
        """Scale coordinates to nanometers."""
        return np.round(coord / px_per_nm).astype(int)

    images = images.assign_coords({"y": scale(images.y), "x": scale(images.x)})
    images["y"] = images.y.assign_attrs(dict(long_name="Height", units="nm"))
    images["x"] = images.x.assign_attrs(dict(long_name="Width", units="nm"))
    dataset = xr.Dataset(coords={images.name: images})
    dataset.to_netcdf(
        path=destination,
        encoding={"images": {"zlib": True}},
    )
    dataset_from_disk = xr.open_dataset(destination)
    ...


if __name__ == "__main__":
    main()
