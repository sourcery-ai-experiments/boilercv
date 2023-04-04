"""Run examples."""

from collections.abc import Callable

from loguru import logger

from boilercv.examples.basic_test import main as main2
from boilercv.examples.blobs.bubbles import main as main4
from boilercv.examples.blobs.galaxy import main as main3
from boilercv.examples.contours.bubbles import main as main6
from boilercv.examples.contours.bubbles_mp4 import main as main5
from boilercv.examples.starry import main as main1


def run_example(func: Callable[[], None]):
    logger.info(f'Running example "{func.__module__}"')
    func()


for func in (main1, main2, main3, main4, main5, main6):
    run_example(func)
