"""Tools for asynchronous execution."""

from asyncio import create_subprocess_shell, create_task, gather
from collections.abc import Awaitable
from pathlib import Path
from subprocess import CompletedProcess
from typing import Any

from dvc.repo import Repo

MODIFIED = [
    Path(path) for path in Repo().data_status(granular=True)["committed"]["modified"]
]


def gather_subprocesses(
    process: str, args: list[str]
) -> Awaitable[list[CompletedProcess[Any]]]:
    """Gather subprocesses which run `proc` against each path in `paths`."""
    return gather(*[run_subprocess(process, args_) for args_ in args])


async def run_subprocess(process: str, args: str):
    """Run a subprocess asynchronously."""
    await create_task(
        (await create_subprocess_shell(f"{process} {args}")).communicate()
    )
