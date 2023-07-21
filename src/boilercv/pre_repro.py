"""Update DVC paths (implicitly through import of PARAMS) and build docs."""

import asyncio
from asyncio import TaskGroup, create_subprocess_exec
from asyncio.subprocess import PIPE
from collections.abc import Callable, Coroutine
from concurrent.futures import ProcessPoolExecutor
from contextlib import AbstractContextManager
from functools import wraps
from os import chdir
from pathlib import Path
from shlex import join, quote, split
from subprocess import CalledProcessError
from typing import Any, TypedDict

from dulwich.porcelain import add  # type: ignore  # pyright: 1.1.311
from dvc.repo import Repo  # type: ignore  # pyright: 1.1.311
from loguru import logger  # type: ignore  # pyright: 1.1.311
from ploomber_engine import execute_notebook  # type: ignore  # pyright: 1.1.311

from boilercv.models.params import PARAMS

RUN_ALL = False
RERUN_COMMITTED = False

CLEAN = True
EXECUTE = False
EXPORT = True
REPORT = False
COMMIT = True
SKIP = not (CLEAN or EXECUTE or EXPORT or REPORT or COMMIT)


async def main():  # noqa: C901
    """Update DVC paths (implicitly through import of PARAMS) and build docs."""

    # Skip if all stages are disabled
    if SKIP:
        return

    # Get notebooks to run
    repo = Repo()
    if RUN_ALL:
        nbs = get_modified_nbs(list(PARAMS.paths.docs.glob("**/*.ipynb")))
    else:
        nbs = get_dvc_modified_nbs(repo)

    # Clean notebooks, removing outputs before execution as necessary
    if CLEAN:
        async with TaskGroup() as tg:
            for nb in nbs:
                tg.create_task(clean_notebook(nb, preserve_outputs=(not EXECUTE)))

    # Repeat the modification check after cleaning
    if not RUN_ALL:
        nbs = get_dvc_modified_nbs(repo)

    # Run CPU-bound stages in a process pool
    if EXECUTE:
        with ProcessPoolExecutor() as executor:
            for nb in nbs:
                executor.submit(log_execution, nb)

    # Run IO-bound stages concurrently (loop is inside the task)
    if EXPORT:
        async with TaskGroup() as tg:
            for nb in nbs:
                tg.create_task(export_notebook(nb))

    # Run the last stage, which requires changing the active directory
    if REPORT:
        workdir = fold(PARAMS.paths.md)
        async with TaskGroup() as tg:
            for kwargs in nbs.values():
                tg.create_task(generate_report_from_notebook(workdir, **kwargs))

    # Commit the changes
    if COMMIT:
        docs_dvc_file = fold(PARAMS.paths.docs.with_suffix(".dvc"))
        repo.commit(docs_dvc_file, force=True)
        add(paths=docs_dvc_file)


async def clean_notebook(nb: str, preserve_outputs: bool):
    """Clean a notebook."""
    for command in [
        f"nbqa black {nb}",
        f"nbqa ruff --fix-only {nb}",
        (
            " nb-clean clean --remove-empty-cells"
            f"{' --preserve-cell-outputs' if preserve_outputs else ''}"
            "   --preserve-cell-metadata ploomber special tags"
            f"  -- {nb}"
        ),
    ]:
        await run_process(command)


def log_execution(nb: str):
    """Log notebook execution."""
    prefix = "Start ploomber-engine execution of "
    logger.info(
        f"{prefix}{nb[:9]}.../" + nb.split("/")[-1]
        if "/" in nb and len(nb) > 30
        else f"{prefix}{nb}"
    )
    return execute_notebook(input_path=nb, output_path=nb)


async def export_notebook(nb: str):
    """Export a notebook to Markdown and HTML."""
    html = fold(PARAMS.local_paths.html)
    md = fold(PARAMS.paths.md)
    for command in [
        f"jupyter-nbconvert {nb} --to markdown --no-input --output-dir {md}",
        f"jupyter-nbconvert {nb} --to html --no-input --output-dir {html}",
    ]:
        await run_process(command)


def preserve_dir(f: Callable[..., Coroutine[Any, Any, Any]]):
    """Preserve the current directory."""

    @wraps(f)
    async def wrapped(*args, **kwargs):
        return await CoroWrapper(f(*args, **kwargs), PreserveDir())

    return wrapped


@preserve_dir
async def generate_report_from_notebook(
    workdir: str, template: str, zotero: str, csl: str, docx: str, md: str
):
    """Generate a DOCX report from a notebook.

    Requires changing the active directory to the Markdown folder outside of this
    asynchronous function, due to how Pandoc generates links inside the documents.
    """
    chdir(workdir)
    await run_process(
        venv=False,
        command=(
            " pandoc"
            # Pandoc configuration
            "   --standalone"  # Don't produce a document fragment.
            "   --from markdown-auto_identifiers"  # Avoids bookmark pollution around Markdown headers
            "   --to docx"  # The output format
            f"  --reference-doc {template}"  # The template to export literature reviews to
            # Zotero Lua filter and metadata passed to it
            f"  --lua-filter {zotero}"  # Needs to be the one downloaded from the tutorial page https://retorque.re/zotero-better-bibtex/exporting/pandoc/#from-markdown-to-zotero-live-citations
            "   --metadata zotero_library:3"  # Corresponds to "Nucleate pool boiling [3]"
            f"  --metadata zotero_csl_style:{csl}"  # Must also be installed in Zotero
            # I/O
            f"  --output {docx}"
            f"  {md}"
        ),
    )


async def run_process(command: str, venv: bool = True):
    """Run a subprocess asynchronously."""
    command, *args = split(command, posix=False)
    cmd_and_args = join([command, *args])
    logger.info(
        f"Start {cmd_and_args[:30]}...{cmd_and_args[-30:]}"
        if len(cmd_and_args) > 60
        else cmd_and_args
    )
    process = await create_subprocess_exec(
        f"{'.venv/scripts/' if venv else ''}{command}", *args, stdout=PIPE, stderr=PIPE
    )
    stdout, stderr = (msg.decode("utf-8") for msg in await process.communicate())
    message = (
        (f"{stdout}\n{stderr}" if stdout and stderr else stdout or stderr)
        .replace("\r\n", "\n")
        .strip()
    )
    if process.returncode:
        exception = CalledProcessError(
            returncode=process.returncode,
            cmd=command,
            output=stdout,
            stderr=stderr,
        )
        exception.add_note(message)
        exception.add_note("Arguments:\n" + "    \n".join(args))
        raise exception
    finish = f"Finish {command}"
    if message:
        indent = "\n    "
        logger.info(
            f"{finish}: ⏎{indent}" + message.replace("\n", indent)
            if "\n" in message
            else f"{finish}: {message}"
        )
    else:
        logger.info(finish)


class ReportKwargs(TypedDict):
    """Keyword arguments for generating a report."""

    template: str
    zotero: str
    csl: str
    docx: str
    md: str


def get_dvc_modified_nbs(repo: Repo) -> dict[str, ReportKwargs]:
    # Check for modifications
    modified = get_dvc_modified(repo, granular=True)
    # Skip if no changes to docs
    return get_modified_nbs(modified) if PARAMS.paths.docs in modified else {}


def get_dvc_modified(repo: Repo, granular: bool = False) -> list[Path]:
    """Get a list of modified files tracked by DVC."""
    status = repo.data_status(granular=granular)
    modified: list[Path] = []
    for key in ["modified", "added"]:
        paths = (status["uncommitted"].get(key) or []) + (
            (status["committed"].get(key) or []) if RERUN_COMMITTED else []
        )
        if paths:
            modified.extend([Path(path) for path in paths])
    return modified


def get_modified_nbs(modified: list[Path]) -> dict[str, ReportKwargs]:
    """Get the modified notebooks and their corresponding report paths."""
    return {
        fold(nb): ReportKwargs(
            **{
                kwarg: fold(path)
                for kwarg, path in dict(
                    template=PARAMS.project_paths.template,
                    zotero=PARAMS.project_paths.zotero,
                    csl=PARAMS.project_paths.csl,
                    docx=PARAMS.paths.docx / nb.with_suffix(".docx").name,
                    md=PARAMS.paths.md / nb.with_suffix(".md").name,
                ).items()
            }
        )
        for nb in sorted(
            [
                path
                for path in modified
                if path.is_relative_to(PARAMS.paths.docs) and path.suffix == ".ipynb"
            ]
        )
    }


def fold(path: Path):
    """Resolve and normalize a path to a POSIX string path with forward slashes."""
    return quote(str(path.resolve()).replace("\\", "/"))


class PreserveDir:
    """Re-entrant context manager that preserves the current directory.

    Reference: <https://stackoverflow.com/a/64395754/20430423>
    """

    def __init__(self):
        self.outer_dir = Path.cwd()
        self.inner_dir = None

    def __enter__(self):
        self.outer_dir = Path.cwd()
        if self.inner_dir is not None:
            chdir(self.inner_dir)

    def __exit__(self, *exception_info_):
        self.inner_dir = Path.cwd()
        chdir(self.outer_dir)


class CoroWrapper:
    """Wrap `target` to have every send issued in a `context`.

    Reference: <https://stackoverflow.com/a/56079900/1600898>
    """

    def __init__(
        self, target: Coroutine[Any, Any, Any], context: AbstractContextManager[Any]
    ):
        self.target = target
        self.context = context

    # wrap an iterator for use with 'await'
    def __await__(self):
        # unwrap the underlying iterator
        target_iter = self.target.__await__()
        # emulate 'yield from'
        iter_send, iter_throw = target_iter.send, target_iter.throw
        send, message = iter_send, None
        while True:
            # communicate with the target coroutine
            try:
                with self.context:  # type: ignore  # pyright: 1.1.311
                    signal = send(message)  # type: ignore  # pyright: 1.1.311
            except StopIteration as err:
                return err.value
            else:
                send = iter_send
            # communicate with the ambient event loop
            try:
                message = yield signal
            except BaseException as err:  # noqa: BLE001
                send, message = iter_throw, err


if __name__ == "__main__":
    logger.add(sink="pre_repro.log")
    logger.info("Start pre_repro")
    asyncio.run(main())
    logger.info("Finish pre_repro")
