"""A setup stage that should be run before DVC pipeline reproduction."""

from pathlib import Path

from ruamel.yaml import YAML

from boilercv.models.paths import Paths

yaml = YAML()
yaml.indent(offset=2)


def main():
    paths = Paths()
    params = yaml.load(paths.file_params) or {}
    params["paths"] = repl_path(paths.dict(exclude_none=True))
    yaml.dump(params, paths.file_params)


def repl_path(dirs_dict: dict[str, Path]):
    """Replace Windows path separator with POSIX separator."""
    return {k: str(v).replace("\\", "/") for k, v in dirs_dict.items()}


if __name__ == "__main__":
    main()
