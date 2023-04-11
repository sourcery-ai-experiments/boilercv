"""Run examples."""

from typing import Any

from boilercv import PREVIEW, run_example
from boilercv.captivate.previews import view_images
from boilercv.examples.cv.basic_test import main as main2
from boilercv.examples.cv.starry import main as main1

results: dict[str, Any] = {}

for func in (main1, main2):
    module_name, result = run_example(func)
    results[module_name] = result

if PREVIEW:
    view_images(results)
