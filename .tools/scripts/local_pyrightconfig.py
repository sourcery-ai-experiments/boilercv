"""Generate a local `pyrightconfig.json` variation for development."""

from json import dumps
from pathlib import Path
from tomllib import loads


def main():
    pyright = loads(Path("pyproject.toml").read_text("utf-8"))["tool"]["pyright"]
    pyright["include"] += [f"../boilercore/{path}" for path in pyright["include"]]
    Path("pyrightconfig.json").write_text(
        encoding="utf-8",
        data=f"{dumps(indent=2, obj=pyright)}\n",
    )
    (Path(".vscode") / "pinned-files.json").write_text(
        encoding="utf-8",
        data='{"version":"2","pinnedList":["c:/Users/Blake/Code/mine/boilercv/data","c:/Users/Blake/Code/mine/boilercv/docs","c:/Users/Blake/Code/mine/boilercv/src/boilercv","c:/Users/Blake/Code/mine/boilercv/tests","c:/Users/Blake/Code/mine/boilercv/dvc_repro.ps1","c:/Users/Blake/Code/mine/boilercv/dvc.yaml","c:/Users/Blake/Code/mine/boilercv/params.yaml"],"aliasMap":{}}',
    )


if __name__ == "__main__":
    main()
