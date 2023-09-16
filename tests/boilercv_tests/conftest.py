"""Test configuration."""

import pytest
from boilercore import ALL_WARNINGS, WarningFilter, filter_certain_warnings
from boilercore.testing import get_session_path

import boilercv


@pytest.fixture(scope="session")
def project_session_path(tmp_path_factory):
    """Set the project directory."""
    return get_session_path(tmp_path_factory, boilercv)


# Can't be session scope
@pytest.fixture(autouse=True)
def _filter_certain_warnings():
    """Filter certain warnings."""
    filter_certain_warnings(
        [
            *ALL_WARNINGS,
            *[
                WarningFilter(
                    message=r"numpy\.ndarray size changed, may indicate binary incompatibility\. Expected \d+ from C header, got \d+ from PyObject",
                    category=RuntimeWarning,
                )
            ],
        ]
    )
