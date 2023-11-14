"""Test configuration."""

from collections import defaultdict
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path
from re import compile
from types import SimpleNamespace
from typing import Any, TypeAlias

import pytest
import pytest_harvest
import seaborn as sns
from boilercore import WarningFilter, filter_certain_warnings
from boilercore.testing import (
    get_accessed_attributes,
    get_cached_nb_namespace,
    get_session_path,
    get_source,
)

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
    yield get_cached_nb_namespace(
        nb=namespace.nb.read_text(encoding="utf-8"),
        params=namespace.params,
        results=get_accessed_attributes(get_source(request.node), request.fixturename),
    )
    update_fixture_stores(
        fixture_stores,
        request.fixturename,
        test=request.node.name,
        path=request.node.path,
    )


FixtureStore: TypeAlias = dict[str, Any]


@dataclass
class FixtureStores:
    """Fixture stores from `pytest-harvest`."""

    flat: FixtureStore
    """The default flat fixture store from `pytest-harvest`."""
    nested: FixtureStore
    """Fixture for test cases, nested by fixture name, module, then node."""


test_case = compile(r"(?P<node>[^\[]+)\[(?P<case>[^\]]+)\]")
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
    if match := test_case.fullmatch(test):
        node, case = match.groups()
        key = f"{path.relative_to(Path.cwd()).as_posix()}::{test}"
        module[node][case] = fixture_stores.flat[fixturename][key]


# * -------------------------------------------------------------------------------- * #
# * Harvest


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
