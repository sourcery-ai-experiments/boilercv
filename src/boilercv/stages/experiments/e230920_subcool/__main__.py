"""Subcooled bubble collapse experiment."""

from concurrent.futures import ProcessPoolExecutor

from boilercore.paths import fold, modified
from ploomber_engine import execute_notebook

from boilercv.models.params import PARAMS
from boilercv.stages.experiments.e230920_subcool import EXP

NB = fold(PARAMS.paths.stages[f"experiments_{EXP}_find_collapse"])
TIMES = [
    "2023-09-20T16:52:06",
    "2023-09-20T16:52:06",
    "2023-09-20T17:01:04",
    "2023-09-20T17:05:15",
    "2023-09-20T17:14:18",
    "2023-09-20T17:26:15",
    "2023-09-20T17:34:38",
    "2023-09-20T17:42:19",
    "2023-09-20T17:47:49",
]


def main():
    if not modified(NB):
        return
    with ProcessPoolExecutor() as executor:
        for time in TIMES:
            executor.submit(
                execute_notebook,
                input_path=NB,
                output_path=None,
                parameters={"TIME": time},
            )


main()
