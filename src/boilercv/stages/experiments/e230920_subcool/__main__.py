"""Subcooled bubble collapse experiment."""

from concurrent.futures import ProcessPoolExecutor

from boilercore.paths import fold, modified
from ploomber_engine import execute_notebook

from boilercv.models.params import PARAMS
from boilercv.stages.experiments.e230920_subcool import EXP, get_times

NB = fold(PARAMS.paths.stages[f"experiments_{EXP}_find_collapse"])
PATHS = (PARAMS.paths.experiments / EXP).iterdir()
TIMES = dict(zip(get_times(path.stem for path in PATHS), PATHS, strict=True))


def main():
    if not modified(NB):
        return
    with ProcessPoolExecutor() as executor:
        for time in TIMES.values():
            executor.submit(
                execute_notebook,
                input_path=NB,
                output_path=None,
                parameters={"TIME": time},
            )


main()
