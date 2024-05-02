"""Convert LaTeX equations to SymPy equations."""

from shlex import quote, split
from subprocess import run

from loguru import logger
from tqdm import tqdm

from boilercv_pipeline.correlations.dimensionless_bubble_diameter.generated import (
    equations,
)
from boilercv_pipeline.equations import LATEX_PARSER, PIPX, SYMPY_REPL


def main():  # noqa: D103
    for expression in tqdm(equations.values()):
        latex = expression.forms.latex
        if not latex:
            continue
        latex = quote(latex.strip().replace("\n", "").replace("    ", ""))
        if expression.forms.sympy:
            continue
    #     toml[EQS][i][SYMPY] = convert_latex_to_sympy(latex)  # pyright: ignore[reportArgumentType, reportIndexIssue]  1.1.356, tomlkit 0.12.4
    # data = dumps(toml)
    # for old, new in TOML_REPL.items():
    #     data = data.replace(old, new)
    # TOML.write_text(encoding="utf-8", data=data)


def convert_latex_to_sympy(latex: str) -> str:
    """Convert LaTeX equation to SymPy equation."""
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
    return eq


if __name__ == "__main__":
    logger.info("Start converting LaTeX expressions to SymPy expressions.")
    main()
    logger.info("Finish converting LaTeX expressions to SymPy expressions.")
