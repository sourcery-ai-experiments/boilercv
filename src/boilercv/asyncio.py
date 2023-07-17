"""Tools for asynchronous execution."""

from asyncio import create_subprocess_shell, create_task, gather
from collections.abc import Awaitable
from subprocess import CompletedProcess
from typing import Any


def gather_subprocesses(commands: list[str]) -> Awaitable[list[CompletedProcess[Any]]]:
    """Gather subprocesses which run `proc` against each path in `paths`."""
    return gather(*[run_subprocess(command) for command in commands])


async def run_subprocess(command: str):
    """Run a subprocess asynchronously."""
    await create_task((await create_subprocess_shell(f"{command}")).communicate())
