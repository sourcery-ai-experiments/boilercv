"""Build the DVC-tracked project documentation."""


from asyncio import run

from boilercv.asyncio import MODIFIED, gather_subprocesses
from boilercv.models.params import PARAMS


async def main():
    await gather_subprocesses(
        f"pwsh {PARAMS.project_paths.script_build_docs}",
        [
            f"{path} {PARAMS.paths.md} {PARAMS.paths.docx}"
            for path in MODIFIED
            if path.suffix == ".ipynb" and path.is_relative_to(PARAMS.paths.docs)
        ],
    )


if __name__ == "__main__":
    run(main())
