"""Cases for experiment `e230920_subcool`."""

from collections.abc import Iterator
from pathlib import Path

from boilercore.paths import get_module_name, walk_module_paths
from boilercore.testing import NotebookCase, get_notebook_cases

from boilercv_tests.cases.e230920_subcool import (
    custom_features,
    find_collapse,
    get_thermal_data,
)

exp = get_module_name(__spec__ or __file__)
modules = dict(
    zip(
        sorted(
            [custom_features, find_collapse, get_thermal_data], key=lambda m: m.__name__
        ),
        sorted(
            walk_module_paths(
                Path(f"src/boilercv/stages/experiments/{exp}"), suffixes=[".ipynb"]
            )
        ),
        strict=True,
    )
)
CASES: dict[str, Iterator[NotebookCase]] = {
    get_module_name(module): get_notebook_cases(notebook, module)
    for module, notebook in modules.items()
}
