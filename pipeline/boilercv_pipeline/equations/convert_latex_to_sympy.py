"""Convert LaTeX equations to SymPy equations."""

from shlex import quote, split
from subprocess import run

from loguru import logger
from tomlkit import dumps, parse
from tqdm import tqdm

from boilercv_pipeline.equations import (
    EQUATIONS,
    LATEX,
    LATEX_PARSER,
    PIPX,
    SYMPY,
    SYMPY_REPL,
    TABLE,
    TOML_REPL,
)


def main():  # noqa: D103
    toml = parse(EQUATIONS.read_text("utf-8"))
    equations = toml[TABLE]
    for i, expression in enumerate(tqdm(equations)):  # pyright: ignore[reportArgumentType, reportCallIssue]  1.1.356, tomlkit 0.12.4
        latex = expression.get(LATEX)
        if not latex:
            continue
        latex = quote(latex.strip().replace("\n", "").replace("    ", ""))
        if expression.get(SYMPY):
            continue
        result = run(
            args=split(f"{PIPX} run {LATEX_PARSER} {latex}"),
            capture_output=True,
            check=False,
            text=True,
        )
        if result.returncode:
            raise RuntimeError(result.stderr)
        eq = result.stdout.strip()
        for old, new in SYMPY_REPL.items():
            eq = eq.replace(old, new)
        toml[TABLE][i][SYMPY] = eq  # pyright: ignore[reportArgumentType, reportIndexIssue]  1.1.356, tomlkit 0.12.4
    data = dumps(toml)
    for old, new in TOML_REPL.items():
        data = data.replace(old, new)
    EQUATIONS.write_text(encoding="utf-8", data=data)


if __name__ == "__main__":
    logger.info("Start converting LaTeX expressions to SymPy expressions.")
    main()
    logger.info("Finish converting LaTeX expressions to SymPy expressions.")
