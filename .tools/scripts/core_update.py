"""Update script to run after core dependencies are installed, but before others."""

from contextlib import closing
from dataclasses import dataclass
from pathlib import Path
from re import MULTILINE, VERBOSE, Pattern, compile
from subprocess import run
from sys import executable, platform

from dulwich.porcelain import submodule_list
from dulwich.repo import Repo

SCRIPTS_DIR = Path(executable).parent
# Version specification
VERSION = r"(?P<version>[^\n]+)"  # e.g. 2.0.2
# Details following a dependency name
DETAIL = r"""(?P<detail>
    (\[[^\]]*\])?  # e.g. [hdf5,performance] (optional)
    [=~><]=        # ==, ~=, >=, <=
    )"""
# Constant regex components
DOMAIN = "git+https://github.com/"
# Pair of dependencies to source and sink version numbers from/to
SRC, DST = "pandas", "pandas-stubs"


def main():
    template, typings_, submodules = get_submodules()
    run(f"{SCRIPTS_DIR}/copier update --defaults --vcs-ref {template.commit}")
    requirements_files = [
        Path("pyproject.toml"),
        *sorted(Path(".tools/requirements").glob("requirements*.txt")),
    ]
    for file in requirements_files:
        original_content = content = file.read_text("utf-8")
        if match := re_spec(rf"{SRC}{DETAIL}{VERSION}").search(content):
            content = re_spec(rf"{DST}{DETAIL}{VERSION}").sub(
                repl=rf"\g<pre>{DST}\g<detail>{match['version']}\g<post>",
                string=content,
            )
        for sub in submodules:
            content = re_spec(
                rf"""
                {sub.name}@                            # name@
                {DOMAIN}
                (?P<org>\w+/)                          # org/
                {sub.name}@                            # name@
                (?P<commit>[^\n]*)                     # <commit-hash>
                $"""
            ).sub(
                repl=rf"\g<pre>{sub.name}@{DOMAIN}\g<org>{sub.name}@{sub.commit}\g<post>",
                string=content,
            )
        if content != original_content:
            file.write_text(encoding="utf-8", data=content)


@dataclass
class Submodule:
    """Represents a git submodule."""

    name: str
    """The submodule name."""
    commit: str
    """The commit hash currently tracked by the submodule."""

    def __post_init__(self):
        """Handle byte strings reported by some submodule sources, like dulwich."""
        # dulwich.porcelain.submodule_list returns bytes
        if isinstance(self.name, bytes):
            self.name = self.name.decode("utf-8")


def get_submodules() -> tuple[Submodule, Submodule, list[Submodule]]:
    """Get the special template and typings submodules, as well as the rest."""
    with closing(repo := Repo(str(Path.cwd()))):
        all_submodules = [Submodule(*item) for item in list(submodule_list(repo))]
    submodules: list[Submodule] = []
    template = typings = None
    for submodule in all_submodules:
        if submodule.name == "template":
            template = submodule
        elif submodule.name == "typings":
            typings = submodule
        else:
            submodules.append(submodule)
    if not template or not typings:
        raise ValueError("Could not find template or typings submodules.")
    return template, typings, submodules


def re_spec(pattern: str) -> Pattern[str]:
    """Specification for a certain regex pattern."""
    # Optional pre and post are for quoted dependencies, as in pyproject.toml
    return compile(
        pattern=rf"""^
                    (?P<pre>\s*['"])?
                    {pattern}
                    (?P<post>\s*['"])?
                    $""",
        flags=VERBOSE | MULTILINE,
    )


if __name__ == "__main__":
    main()
