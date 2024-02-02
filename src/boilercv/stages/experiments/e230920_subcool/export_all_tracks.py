"""Export all objects for this experiment."""

from concurrent.futures import ProcessPoolExecutor

from boilercv.stages.experiments.e230920_subcool import EXP_TIMES, export_tracks


def main():
    with ProcessPoolExecutor() as executor:
        for dt in EXP_TIMES:
            executor.submit(
                export_tracks,
                params={
                    "GET_TRACKPY_TRACKS": False,
                    "TIME": dt.isoformat(),
                    "FRAMES": None,
                },
            )


if __name__ == "__main__":
    main()
