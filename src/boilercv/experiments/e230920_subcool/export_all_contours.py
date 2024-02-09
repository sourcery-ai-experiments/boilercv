"""Export all contours for this experiment."""

from concurrent.futures import ProcessPoolExecutor

from boilercv.experiments.e230920_subcool import EXP_TIMES, export_contours


def main():
    with ProcessPoolExecutor() as executor:
        for dt in EXP_TIMES:
            executor.submit(export_contours, params={"TIME": dt.isoformat()})


if __name__ == "__main__":
    main()
