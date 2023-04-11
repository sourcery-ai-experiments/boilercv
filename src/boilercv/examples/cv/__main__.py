"""Run examples."""

from boilercv import run_example
from boilercv.examples.cv.basic_test import main as main2
from boilercv.examples.cv.starry import main as main1

for func in (main1, main2):
    run_example(func)
