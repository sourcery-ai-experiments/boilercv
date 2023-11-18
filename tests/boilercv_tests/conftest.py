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

import pytest
import pytest_harvest
import seaborn as sns
from boilercore import WarningFilter, filter_certain_warnings
from boilercore.notebooks.namespaces import get_cached_minimal_nb_ns
from boilercore.testing import get_session_path, unwrap_node

import boilercv
from boilercv_tests import NsArgs

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


@pytest.fixture()
@pytest_harvest.saved_fixture
def ns(request, fixture_stores) -> Iterator[SimpleNamespace]:
    """Notebook namespace."""
    namespace: NsArgs = request.param
    yield get_cached_minimal_nb_ns(
        nb=namespace.nb.read_text(encoding="utf-8"),
        receiver=unwrap_node(request.node),
        params=namespace.params,
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

RESULTS_PATH = Path(f".xdist_harvested/{getpid()}")
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
    """Delete all temporary pickle files."""
    rmtree(RESULTS_PATH, ignore_errors=True)
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
def fig_ax(plt):
    """Plot."""
    fig, ax = plt.subplots()
    return fig, ax


@pytest.fixture()
def fig(fig_ax):
    """Plot."""
    return fig_ax[0]


@pytest.fixture()
def ax(fig_ax):
    """Plot."""
    return fig_ax[1]
