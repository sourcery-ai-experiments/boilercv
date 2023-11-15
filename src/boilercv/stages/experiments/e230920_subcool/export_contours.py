"""Export contours for this experiment."""

from concurrent.futures import ProcessPoolExecutor

from boilercore.paths import fold
from ploomber_engine import execute_notebook

from boilercv.models.params import PARAMS
from boilercv.stages.experiments.e230920_subcool import EXP, get_times


def main():
    export_contours = fold(
        PARAMS.paths.stages[f"experiments_{EXP}_export_contours"].with_suffix(".ipynb")
    )
    with ProcessPoolExecutor() as executor:
        for dt in get_times(
            path.stem for path in (PARAMS.paths.experiments / EXP).iterdir()
        ):
            executor.submit(
                execute_notebook,
                input_path=export_contours,
                output_path=None,
                parameters={"TIME": dt.isoformat().replace(":", "-")},
            )


if __name__ == "__main__":
    main()
