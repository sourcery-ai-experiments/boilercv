"""Export all centers for this experiment."""

from concurrent.futures import ProcessPoolExecutor

from boilercv.stages.experiments.e230920_subcool import EXP_TIMES, export_centers


def main():
    with ProcessPoolExecutor() as executor:
        for dt in EXP_TIMES:
            executor.submit(
                export_centers,
                params={
                    "GET_TRACKPY_CENTERS": False,
                    "TIME": dt.isoformat(),
                    "FRAMES": None,
                },
            )


if __name__ == "__main__":
    main()
