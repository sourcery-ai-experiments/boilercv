"""Example of converting CINE files to the NetCDF file format."""


from boilercv import EXAMPLE_BIG_CINE
from boilercv.data.dataset import assign_length_dims, prepare_dataset
from boilercv.models.params import PARAMS

NUM_FRAMES = 100


def main():
    source = EXAMPLE_BIG_CINE
    destination = PARAMS.paths.examples / f"{source.stem}.nc"
    dataset = prepare_dataset(source, num_frames=NUM_FRAMES)
    assign_length_dims(dataset)
    dataset.to_netcdf(
        path=destination,
        # encoding={images.name: {"zlib": True}},
    )


if __name__ == "__main__":
    main()
