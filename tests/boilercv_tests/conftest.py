"""Test configuration."""

import pickle
from collections import defaultdict
from collections.abc import Iterator
from dataclasses import dataclass
from logging import warning
from os import getpid
from pathlib import Path
from re import compile
from shutil import rmtree
from types import SimpleNamespace
from typing import Any, TypeAlias

import boilercv
import pytest
import pytest_harvest
import seaborn as sns
from _pytest.python import Function
from boilercore import WarningFilter, filter_certain_warnings
from boilercore.notebooks.namespaces import get_cached_nb_ns, get_ns_attrs
from boilercore.testing import get_session_path
from matplotlib.axis import Axis
from matplotlib.figure import Figure

from boilercv_tests import Case, normalize_cases

CASES_VAR = "CASES"
"""Module-level variable in test modules containing notebook cases for that module."""

# * -------------------------------------------------------------------------------- * #
# * Autouse


@pytest.fixture(autouse=True, scope="session")
def _project_session_path(tmp_path_factory):
    """Set project directory."""
    get_session_path(tmp_path_factory, boilercv)


# Can't be session scope
@pytest.fixture(autouse=True)
def _filter_certain_warnings():
    """Filter certain warnings."""
    filter_certain_warnings(
        [
            WarningFilter(
                message=r"numpy\.ndarray size changed, may indicate binary incompatibility\. Expected \d+ from C header, got \d+ from PyObject",
                category=RuntimeWarning,
            ),
            WarningFilter(
                message=r"A grouping was used that is not in the columns of the DataFrame and so was excluded from the result\. This grouping will be included in a future version of pandas\. Add the grouping as a column of the DataFrame to silence this warning\.",
                category=FutureWarning,
            ),
        ]
    )


# * -------------------------------------------------------------------------------- * #
# * Notebook namespaces


@pytest.fixture(scope="module", autouse=True)
def _get_ns_attrs(request):
    module = request.module
    cases = getattr(module, CASES_VAR, [])
    notebook_namespace_tests = (
        node
        for node in request.node.collect()
        if isinstance(node, Function) and "ns" in node.fixturenames
    )
    for case, test in zip(cases, notebook_namespace_tests, strict=True):
        name = getattr(module, test.originalname)
        case.results |= {r: None for r in get_ns_attrs(name)}
    normalize_cases(*cases)


@pytest.fixture()
@pytest_harvest.saved_fixture
def ns(request, fixture_stores) -> Iterator[SimpleNamespace]:
    """Notebook namespace."""
    case: Case = request.param
    yield get_cached_nb_ns(
        nb=case.nb, params=case.params, attributes=case.results.keys()
    )
    update_fixture_stores(
        fixture_stores,
        request.fixturename,
        test=request.node.name,
        path=request.node.path,
    )


# * -------------------------------------------------------------------------------- * #
# * Harvest

FixtureStore: TypeAlias = dict[str, Any]


@dataclass
class FixtureStores:
    """Fixture stores from `pytest-harvest`."""

    flat: FixtureStore
    """The default flat fixture store from `pytest-harvest`."""
    nested: FixtureStore
    """Fixture for test cases, nested by fixture name, module, then node."""


TEST_CASE = compile(r"(?P<node>[^\[]+)\[(?P<case>[^\]]+)\]")
"""Pattern for e.g. `test[case]`."""


def update_fixture_stores(
    fixture_stores: FixtureStores, fixturename: str, test: str, path: Path
):
    """Update nested fixture store with the new namespace."""
    module = fixture_stores.nested[fixturename][
        path.relative_to(Path("tests/boilercv_tests").resolve())
        .with_suffix("")
        .as_posix()
    ]
    if match := TEST_CASE.fullmatch(test):
        node, case = match.groups()
        key = f"{path.relative_to(Path.cwd()).as_posix()}::{test}"
        module[node][case] = fixture_stores.flat[fixturename][key]


@pytest.fixture(scope="session")
def fixtures(nested_fixture_store) -> SimpleNamespace:
    return SimpleNamespace(
        **{
            key: SimpleNamespace(
                **{
                    key: SimpleNamespace(
                        **{
                            key: SimpleNamespace(**value)
                            for key, value in value.items()
                        }
                    )
                    for key, value in value.items()
                }
            )
            for key, value in nested_fixture_store.items()
        }
    )


@pytest.fixture(scope="session")
def nested_fixture_store(fixture_stores) -> FixtureStore:
    return fixture_stores.nested


@pytest.fixture(scope="session")
def fixture_stores(fixture_store) -> FixtureStores:
    return FixtureStores(
        flat=fixture_store,
        nested=defaultdict(
            lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(dict)))
        ),
    )


# * -------------------------------------------------------------------------------- * #
# * Harvest hooks
# #   https://github.com/smarie/python-pytest-harvest/issues/46#issuecomment-742367746
# #   https://smarie.github.io/python-pytest-harvest/#pytest-x-dist

HARVEST_ROOT = Path(".xdist_harvested")
HARVEST_ROOT.mkdir(exist_ok=True)
RESULTS_PATH = HARVEST_ROOT / str(getpid())
RESULTS_PATH.mkdir(exist_ok=True)


def pytest_harvest_xdist_init():
    """Reset the recipient folder."""
    if RESULTS_PATH.exists():
        rmtree(RESULTS_PATH)
    RESULTS_PATH.mkdir(exist_ok=False)
    return True


def pytest_harvest_xdist_worker_dump(worker_id, session_items, fixture_store):
    """Persist session_items and fixture_store in the file system."""
    with (RESULTS_PATH / f"{worker_id}.pkl").open("wb") as f:
        try:
            pickle.dump((session_items, fixture_store), f)
        except Exception as e:  # noqa: BLE001
            warning(  # noqa: PLE1206
                "Error while pickling worker %s's harvested results: " "[%s] %s",
                (worker_id, e.__class__, e),
            )
    return True


def pytest_harvest_xdist_load():
    """Restore the saved objects from file system."""
    workers_saved_material = {}
    for pkl_file in RESULTS_PATH.glob("*.pkl"):
        wid = pkl_file.stem
        with pkl_file.open("rb") as f:
            workers_saved_material[wid] = pickle.load(f)
    return workers_saved_material


def pytest_harvest_xdist_cleanup():
    """Don't clean up. Fails to delete directories often."""
    return True


# * -------------------------------------------------------------------------------- * #
# * Plot


@pytest.fixture()
def plt(plt):
    """Plot."""
    sns.set_theme(
        context="notebook", style="whitegrid", palette="bright", font="sans-serif"
    )
    yield plt
    plt.saveas = f"{plt.saveas[:-4]}.png"


@pytest.fixture()
def fig_ax(plt) -> tuple[Figure, Axis]:
    """Plot figure and axis."""
    fig, ax = plt.subplots()
    return fig, ax


@pytest.fixture()
def fig(fig_ax) -> Figure:
    """Plot figure."""
    return fig_ax[0]


@pytest.fixture()
def ax(fig_ax) -> Axis:
    """Plot axis."""
    return fig_ax[1]
