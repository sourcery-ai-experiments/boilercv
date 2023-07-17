"""Build the DVC-tracked project documentation."""

from asyncio import run

from boilercv.asyncio import gather_subprocesses
from boilercv.dvc import REPO, get_dvc_modified
from boilercv.models.params import PARAMS


async def main():
    await gather_subprocesses(
        [
            (
                "pwsh"
                f" {PARAMS.project_paths.script_build_docs}"
                f" {path} {PARAMS.paths.md} {PARAMS.paths.docx}"
                f" {PARAMS.local_paths.html.expanduser()}"
            )
            for path in get_dvc_modified(REPO, granular=True, committed=True)
            if path.is_relative_to(PARAMS.paths.docs) and path.suffix == ".ipynb"
        ],
    )


if __name__ == "__main__":
    run(main())
