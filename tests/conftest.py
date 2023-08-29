"""Test configuration."""

from pathlib import Path

import pytest
from boilercore.testing import tmp_workdir


@pytest.fixture(autouse=True)
def _tmp_workdir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """Produce a temporary project directory."""
    tmp_workdir(tmp_path, monkeypatch)
