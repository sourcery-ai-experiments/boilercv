"""Export all objects for this experiment."""

from concurrent.futures import ProcessPoolExecutor

from boilercv.experiments.e230920_subcool import EXP_TIMES, submit_nb_process


def main():
    with ProcessPoolExecutor() as executor:
        for dt in EXP_TIMES:
            submit_nb_process(
                executor=executor,
                nb="find_objects",
                name="objects",
                params={
                    "FRAMES": None,
                    "GET_TRACKPY_CENTERS": False,
                    "TIME": dt.isoformat(),
                },
            )


if __name__ == "__main__":
    main()
