from pathlib import Path

import cv2 as cv

Path("build.txt").write_text(cv.getBuildInformation(), encoding="utf-8")
