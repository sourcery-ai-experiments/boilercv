"""Update DVC paths (implicitly through import of PARAMS) and build docs."""

import asyncio
from asyncio import TaskGroup, create_subprocess_exec
from asyncio.subprocess import PIPE
from collections.abc import Callable, Coroutine
from concurrent.futures import ProcessPoolExecutor  # noqa: F401
from contextlib import AbstractContextManager
from functools import wraps
from os import chdir
from pathlib import Path
from shlex import quote, split
from subprocess import CalledProcessError
from sys import stdout
from typing import Any

from dulwich.porcelain import add  # type: ignore  # pyright: 1.1.311
from dvc.repo import Repo  # type: ignore  # pyright: 1.1.311
from loguru import logger  # type: ignore  # pyright: 1.1.311

from boilercv.models.params import PARAMS

DOCS = PARAMS.paths.docs
RUN_ALL = ALSO_RUN_COMMITTED = True
CLEAN = EXECUTE = EXPORT = REPORT = COMMIT = True

REPLAY_LOG = True
file = Path("pre_repro.log")
logger.remove()
if REPLAY_LOG:
    logger.add(
        sink=file,
        format=(r"\<green>{time:YYYY-MM-DD HH:mm:ss}\</green> | {message}"),
    )
    logger = logger.opt(colors=False)
else:
    for sink in [stdout, file]:
        logger.add(
            sink=sink,
            format=(
                "<green>{time:YYYY-MM-DD HH:mm:ss}</green> |"
                # " <level>{level: <8}</level> |"
                # " <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> -"
                " {message}"
            ),
        )
    logger = logger.opt(colors=True)


async def main():
    # Check for modifications
    if skip_ := not (CLEAN or EXECUTE or EXPORT or REPORT or COMMIT):
        return
    repo = Repo()
    if RUN_ALL:
        nbs = fold_docs_nbs(list(DOCS.glob("**/*.ipynb")), DOCS)
    else:
        nbs = fold_modified_nbs(repo, ALSO_RUN_COMMITTED, DOCS)

    async with TaskGroup() as tg:
        for nb in nbs.items():
            tg.create_task(process_notebook(nb))

    # Commit changes
    if COMMIT:
        docs_dvc_file = fold(DOCS.with_suffix(".dvc"))
        repo.commit(docs_dvc_file, force=True)
        add(paths=docs_dvc_file)


async def process_notebook(nb: tuple[Path, str]):
    await clean_notebook(nb[1], preserve_outputs=True, lint=True)
    await export_notebook(
        nb[1], html=fold(PARAMS.local_paths.html), md=fold(PARAMS.paths.md)
    )
    await generate_report_from_notebook(
        **{
            kwarg: fold(path)
            for kwarg, path in dict(
                workdir=PARAMS.paths.md,
                template=PARAMS.project_paths.template,
                zotero=PARAMS.project_paths.zotero,
                csl=PARAMS.project_paths.csl,
                docx=PARAMS.paths.docx / nb[0].with_suffix(".docx").name,
                md=PARAMS.paths.md / nb[0].with_suffix(".md").name,
            ).items()
        },
    )


async def clean_notebook(nb: str, preserve_outputs: bool, lint: bool):
    """Clean a notebook."""
    commands = [f"nbqa black {nb}", f"nbqa ruff --fix-only {nb}"] if lint else []
    commands.append(
        "   nb-clean clean --remove-empty-cells"
        f"{'  --preserve-cell-outputs' if preserve_outputs else ''}"
        "     --preserve-cell-metadata special tags"
        f"    -- {nb}"
    )
    for command in commands:
        await run_process(command)


async def export_notebook(nb: str, md: str, html: str):
    """Export a notebook to Markdown and HTML."""
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


COLORS = {
    "jupyter-nbconvert": "cyan",
    "nb-clean": "magenta",
    "nbqa": "yellow",
    "pandoc": "blue",
}


async def run_process(command: str, venv: bool = True):
    """Run a subprocess asynchronously."""
    command, *args = split(command, posix=False)

    # Log start
    file = args[-1].split("/")[-1]
    colored_command = f"<{COLORS[command]}>{command}</{COLORS[command]}>"
    logger.info(f"<yellow>Start </yellow> {colored_command} {file}")

    # Run process
    process = await create_subprocess_exec(
        f"{'.venv/scripts/' if venv else ''}{command}", *args, stdout=PIPE, stderr=PIPE
    )
    stdout, stderr = (msg.decode("utf-8") for msg in await process.communicate())
    message = (
        (f"{stdout}\n{stderr}" if stdout and stderr else stdout or stderr)
        .replace("\r\n", "\n")
        .strip()
    )

    # Handle exceptions
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

    # Log finish
    logger.info(
        f"<green>Finish</green> {colored_command} {file}"
        + ((": " + message.replace("\n", ". ")[:30] + "...") if message else "")
    )


def fold_modified_nbs(repo: Repo, also_committed: bool, docs: Path) -> dict[Path, str]:
    """Fold the paths of modified documentation notebooks."""
    modified = get_modified_files(repo, also_committed)
    return fold_docs_nbs(modified, docs) if docs in modified else {}


def get_modified_files(repo: Repo, also_committed: bool) -> list[Path]:
    """Get files considered modified by DVC."""
    status = repo.data_status(granular=True)
    modified: list[Path] = []
    for key in ["modified", "added"]:
        paths = status["uncommitted"].get(key) or []
        if also_committed:
            paths.extend(status["committed"].get(key) or [])
        modified.extend([Path(path) for path in paths])
    return modified


def fold_docs_nbs(paths: list[Path], docs: Path) -> dict[Path, str]:
    """Fold the paths of documentation-related notebooks."""
    return {
        nb: fold(nb)
        for nb in sorted(
            [
                path
                for path in paths
                if path.is_relative_to(docs) and path.suffix == ".ipynb"
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
    asyncio.run(main())
    logger.info("<green>FINISH</green> pre_repro")
