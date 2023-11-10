"""Test configuration."""

from collections.abc import Callable
from types import SimpleNamespace
from typing import Any, TypeAlias

import pytest
from boilercore import WarningFilter, filter_certain_warnings
from boilercore.testing import get_nb_client, get_nb_namespace, get_session_path

import boilercv


@pytest.fixture(autouse=True, scope="session")
def project_session_path(tmp_path_factory):
    """Set the project directory."""
    return get_session_path(tmp_path_factory, boilercv)


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


Check: TypeAlias = Callable[[SimpleNamespace], Any]
Ns: TypeAlias = SimpleNamespace


@pytest.fixture()
def cases(request) -> tuple[Ns, Check]:
    path, parameters, fun = request.param
    return get_nb_namespace(get_nb_client(path), parameters), fun
