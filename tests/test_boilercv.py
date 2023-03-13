from cv2 import version
from dvc.repo import Repo


def test_repro():
    """Test that the pipeline can be reproduced."""
    Repo().reproduce(pull=True)  # type: ignore  # upstream


def test_contrib():
    """Ensure the installed version of OpenCV has extras.

    Dependencies can specify a different version of OpenCV than the one required in this
    project, unintentionally clobbering the installed version of OpenCV. Detect whether
    a non-`contrib` version is installed by a dependency.
    """
    assert version.contrib
