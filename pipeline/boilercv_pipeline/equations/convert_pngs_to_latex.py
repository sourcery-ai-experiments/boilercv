"""Convert PNGs to LaTeX."""

from shlex import quote, split
from subprocess import run

from loguru import logger
from tomlkit import dumps, parse
from tqdm import tqdm

from boilercv_pipeline.equations import (
    EQUATIONS,
    INDEX,
    LATEX,
    LATEX_REPL,
    NAME,
    PIPX,
    PNG_PARSER,
    PNGS,
    TABLE,
    TOML_REPL,
)


def main():  # noqa: D103
    toml = parse(EQUATIONS.read_text("utf-8"))
    equations = toml[TABLE]
    for i, expression in enumerate(tqdm(equations)):  # pyright: ignore[reportArgumentType, reportCallIssue]  1.1.356, tomlkit 0.12.4
        name = expression.get(NAME)
        if not name:
            continue
        name = name.strip().replace("\n", "").replace("    ", "")
        png = PNGS / f"{name}.png"
        if not png.exists() or expression.get(LATEX):
            continue
        sep = " "
        result = run(
            args=split(
                sep.join([
                    f"{PIPX} run --pip-args '--extra-index-url {INDEX}' --",
                    f"{PNG_PARSER} {quote(png.as_posix())}",
                ])
            ),
            capture_output=True,
            check=False,
            text=True,
        )
        if result.returncode:
            raise RuntimeError(result.stderr)
        latex = result.stdout.strip()
        for old, new in LATEX_REPL.items():
            latex = latex.replace(old, new)
        toml[TABLE][i][LATEX] = latex  # pyright: ignore[reportArgumentType, reportIndexIssue]  1.1.356, tomlkit 0.12.4
    data = dumps(toml)
    for old, new in TOML_REPL.items():
        data = data.replace(old, new)
    EQUATIONS.write_text(encoding="utf-8", data=data)


if __name__ == "__main__":
    logger.info("Start making equations from clipboard.")
    main()
    logger.info("Finish making equations from clipboard.")
