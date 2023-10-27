"""Generate reports."""

import asyncio

from boilercore.notebooks.report import generate
from dvc.repo import Repo

from boilercv.models.params import PARAMS


def main():
    asyncio.run(generate(PARAMS.paths, Repo()))


if __name__ == "__main__":
    main()
