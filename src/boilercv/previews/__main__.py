"""Run examples for the `boilercv.previews` module."""

# ruff: noqa: I001

from pathlib import Path

from boilercv import FRAMERATE_PREV, PREVIEW, WRITE, run_example
from boilercv.captivate.captures import write_video
from boilercv.captivate.previews import view_images
from boilercv.models.params import LOCAL_PATHS
from boilercv.types import DA

from boilercv.previews.gray import main as main1
from boilercv.previews.binarized import main as main2
from boilercv.previews.composite import main as main3
from boilercv.previews.filled import main as main4

results: dict[str, DA] = {}

for func in (main1, main2, main3, main4):
    module_name, result = run_example(func)
    results[module_name] = result
    if WRITE:
        module_path = Path(module_name.replace(".", "/").removeprefix("boilercv/"))
        path = LOCAL_PATHS.media / module_path
        path.parent.mkdir(parents=True, exist_ok=True)
        write_video(path, result, framerate=FRAMERATE_PREV)

if PREVIEW:
    view_images(results, framerate=FRAMERATE_PREV)
