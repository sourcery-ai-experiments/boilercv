"""Run examples."""

from collections.abc import Callable

from loguru import logger

from boilercv.examples.basic_test import main as main2
from boilercv.examples.contours import main as main3
from boilercv.examples.starry import main as main1


def run_example(func: Callable[[], None]):
    logger.info(f'Running example "{func.__module__}"')
    func()


for func in (main1, main2, main3):
    run_example(func)
