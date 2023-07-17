"""Prepare to reproduce the pipeline with DVC."""

from subprocess import run

from dulwich.porcelain import add

from boilercv.dvc import REPO, get_dvc_modified
from boilercv.models.params import PARAMS


def main():
    if PARAMS.paths.docs in get_dvc_modified(REPO):
        run(f"pwsh {PARAMS.project_paths.script_repair_notebooks}")  # noqa: S603
        docs_dvc_file = PARAMS.paths.docs.with_suffix(".dvc")
        REPO.commit(str(docs_dvc_file), force=True)
        add(paths=str(docs_dvc_file))


if __name__ == "__main__":
    main()
