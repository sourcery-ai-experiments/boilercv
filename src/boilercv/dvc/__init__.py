"""Setup for DVC operations."""

from pathlib import Path

from dvc.repo import Repo

REPO = Repo()


def get_dvc_modified(
    repo: Repo, granular: bool = False, committed: bool = False
) -> list[Path]:
    """Get a list of modified files tracked by DVC."""
    status = repo.data_status(granular=granular)
    modified = status["committed" if committed else "uncommitted"].get("modified")
    return [Path(path) for path in modified] if modified else []
