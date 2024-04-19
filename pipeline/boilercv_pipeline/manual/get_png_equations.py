"""Create PNGs for new equations in `equations.toml`."""

from copykitten import paste_image
from loguru import logger
from PIL import Image
from tomlkit import dumps, parse
from tqdm import tqdm

from boilercv_pipeline.manual import EQUATIONS, PNGS, TABLE

NAME = "name"
"""Key for equation names in the equations TOML file."""


def main():  # noqa: D103
    toml = parse(EQUATIONS.read_text("utf-8"))
    equations = toml[TABLE]
    for expression in tqdm(equations):  # pyright: ignore[reportArgumentType, reportCallIssue]  1.1.356, tomlkit 0.12.4
        name = expression.get(NAME)
        png = PNGS / f"{name}.png"
        if not name or png.exists():
            continue
        input(f"\n\nPlease snip equation `{name}` to your clipboard...")
        pixels, width, height = paste_image()
        img = Image.frombytes(mode="RGBA", size=(width, height), data=pixels)
        img.convert("RGB").save(png)
    EQUATIONS.write_text(encoding="utf-8", data=dumps(toml))


if __name__ == "__main__":
    logger.info("Start making equations from clipboard.")
    main()
    logger.info("Finish making equations from clipboard.")
