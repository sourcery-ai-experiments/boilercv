"""Setup for DVC operations."""

from pathlib import Path

from dvc.repo import Repo

REPO = Repo()


def get_dvc_modified(
    repo: Repo, granular: bool = False, committed: bool = False
) -> list[Path]:
    """Get a list of modified files tracked by DVC."""
    status = repo.data_status(granular=granular)
    modified: list[Path] = []
    for key in ["modified", "added"]:
        if paths := status["committed" if committed else "uncommitted"].get(key):
            modified.extend([Path(path) for path in paths])
    return modified
