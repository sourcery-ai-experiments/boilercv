"""Convert LaTeX equations to SymPy equations."""

from pathlib import Path
from shlex import quote, split
from subprocess import run

from loguru import logger
from tomlkit import dumps, parse
from tqdm import tqdm

from boilercv_pipeline.manual import EQUATIONS, SYMPY, TABLE

LATEX = "latex"
"""Key for LaTeX expressions in the equations TOML file."""
PIPX = (Path(".venv") / "scripts" / "pipx").as_posix()
"""Escaped path to `pipx` executable suitable for `subprocess.run` invocation."""
PARSER = (Path("scripts") / "parse_latex.py").as_posix()
"""Escaped path to parser script suitable for `subprocess.run` invocation."""


def main():  # noqa: D103
    toml = parse(EQUATIONS.read_text("utf-8"))
    equations = toml[TABLE]
    for i, expression in enumerate(tqdm(equations)):  # pyright: ignore[reportArgumentType, reportCallIssue]  1.1.356, tomlkit 0.12.4
        latex = quote(expression.get(LATEX).replace("\n", ""))
        if not latex or expression.get(SYMPY):
            continue
        result = run(
            args=split(f"{PIPX} run {PARSER} {latex}"),
            capture_output=True,
            check=False,
            text=True,
        )
        if result.returncode:
            raise RuntimeError(result.stderr)
        toml[TABLE][i][SYMPY] = result.stdout.strip()  # pyright: ignore[reportArgumentType, reportIndexIssue]  1.1.356, tomlkit 0.12.4
    EQUATIONS.write_text(encoding="utf-8", data=dumps(toml))


if __name__ == "__main__":
    logger.info("Start converting LaTeX expressions to SymPy expressions.")
    main()
    logger.info("Finish converting LaTeX expressions to SymPy expressions.")
