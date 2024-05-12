"""Convert LaTeX equations to SymPy equations."""

from collections.abc import Mapping
from pathlib import Path
from shlex import quote, split
from subprocess import run

from cyclopts import App
from loguru import logger
from numpy import finfo
from sympy import sympify
from tomlkit import dumps, parse
from tomlkit.items import Table
from tqdm import tqdm

from boilercv_pipeline.correlations import PIPX
from boilercv_pipeline.correlations.dimensionless_bubble_diameter.equations import (
    EQUATIONS,
    EQUATIONS_TOML,
    MAKE_RAW,
    Forms,
    FormsD,
    FormsM,
    FormsRepl,
    K,
    Kind,
    V_co,
    regex_replace,
    set_equation_forms,
)
from boilercv_pipeline.correlations.dimensionless_bubble_diameter.symbolic import LOCALS

APP = App()
"""CLI."""


def main():  # noqa: D103
    APP()


@APP.default
def default(overwrite: bool = False):  # noqa: D103
    latex_parser = Path("scripts") / "convert_latex_to_sympy.py"
    latex = "latex"
    symbolic = "sympy"
    data = EQUATIONS_TOML.read_text("utf-8")
    raw_all_single_quoted = '"' not in data
    toml = parse(data)
    for name, raw in tqdm(
        ((name, Forms(equation)) for name, equation in EQUATIONS.items())
    ):
        if not raw.get(latex):
            continue
        sanitized = raw.pipe(set_equation_forms, symbolic=symbolic)
        if sanitized.get(symbolic) and not overwrite:
            continue
        changed = (
            sanitized.pipe(convert, PIPX, latex_parser, latex, symbolic)
            .pipe(set_equation_forms, symbolic)
            .pipe(compare, orig=sanitized)
            .pipe(remove_symbolically_equiv, orig=sanitized, symbolic=symbolic)
        )
        if overwrite or changed:
            for kind, eq in changed.items():
                if (table := toml.get(name)) and isinstance(table, Table):
                    table[kind] = eq
    data = dumps(toml)
    if raw_all_single_quoted and r"\"" not in data:
        for old, new in MAKE_RAW.items():
            data = data.replace(old, new)
    EQUATIONS_TOML.write_text(encoding="utf-8", data=data)


def convert(
    i: FormsM, interpreter: Path, script: Path, latex: Kind, symbolic: Kind
) -> FormsD:
    """Convert LaTeX equation to SymPy equation."""
    sanitized_latex = regex_replace(
        i,
        tuple(
            FormsRepl(src=latex, dst=latex, find=find, repl=repl)
            for find, repl in {r"\\left\(": "(", r"\\right\)": ")"}.items()
        ),
    )[latex]
    result = run(
        args=split(
            f"{escape(interpreter)} run {escape(script)} {quote(sanitized_latex)}"
        ),
        capture_output=True,
        check=False,
        text=True,
    )
    if result.returncode:
        raise RuntimeError(result.stderr)
    i = dict(i)
    i[symbolic] = result.stdout.strip()
    return i


def compare(i: Mapping[K, V_co], orig: Mapping[K, V_co]) -> dict[K, V_co]:
    """Compare, returning only the subset that changed."""
    return {k: v for k, v in i.items() if v != orig[k]}


def escape(path: Path) -> str:
    """Escape path for running subprocesses."""
    return quote(path.as_posix())


def remove_symbolically_equiv(i: FormsM, orig: FormsM, symbolic: Kind) -> FormsD:
    """Remove symbolically equivalent forms."""
    i = dict(i)
    old_eq = orig.get(symbolic)
    eq = i.get(symbolic)
    if not old_eq or not eq:
        return i
    old = sympify(old_eq, locals=LOCALS, evaluate=False)
    new = sympify(eq, locals=LOCALS, evaluate=False)
    compare = (old.lhs - old.rhs) - (new.lhs - new.rhs)
    if compare == 0:
        # ? Equations compare equal without simplifying
        i.pop(symbolic)
        return i
    compare = compare.simplify()
    if compare == 0:
        # ? Equations compare equal after simplifying
        i.pop(symbolic)
        return i
    compare = compare.evalf(subs=dict.fromkeys(LOCALS, 1))
    if complex(compare).real < finfo(float).eps:
        # ? Equations compare equal within machine after unit substitution
        i.pop(symbolic)
        return i
    # ? Equations are not symbolically equivalent
    return i


if __name__ == "__main__":
    logger.info("Start converting LaTeX expressions to SymPy expressions.")
    main()
    logger.info("Finish converting LaTeX expressions to SymPy expressions.")
