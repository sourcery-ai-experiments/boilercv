"""Example of converting CINE files to the NetCDF file format."""

from boilercv.models.params import PARAMS
from boilercv.video.cine import convert_cine_to_netcdf


def main():
    variable_name = "images"
    source = PARAMS.paths.examples / "results_2022-11-30T12-39-07_98C.cine"
    destination = PARAMS.paths.examples / f"{source.stem}.nc"
    return convert_cine_to_netcdf(variable_name, source, destination)


if __name__ == "__main__":
    main()
