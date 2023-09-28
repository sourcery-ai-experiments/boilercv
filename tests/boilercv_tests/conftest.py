"""Test configuration."""

from pathlib import Path

import pytest
from boilercore import WarningFilter, filter_certain_warnings
from boilercore.testing import get_nb_client, get_session_path
from ploomber_engine.ipython import PloomberClient

import boilercv
from boilercv_tests import nbs_to_execute


@pytest.fixture(autouse=True, scope="session")
def project_session_path(tmp_path_factory):
    """Set the project directory."""
    return get_session_path(tmp_path_factory, boilercv)


# Can't be session scope
@pytest.fixture(autouse=True)
def _filter_certain_warnings():
    """Filter certain warnings."""
    filter_certain_warnings(
        package=boilercv.__name__,
        warnings=[
            WarningFilter(
                message=r"numpy\.ndarray size changed, may indicate binary incompatibility\. Expected \d+ from C header, got \d+ from PyObject",
                category=RuntimeWarning,
            )
        ],
    )


@pytest.fixture(params=nbs_to_execute)
def nb_to_execute(request) -> Path:
    """Path to a notebook that should be executed only."""
    return request.param


@pytest.fixture()
def nb_client_to_execute(nb_to_execute) -> PloomberClient:
    """Notebook client to be executed only."""
    return get_nb_client(nb_to_execute)
