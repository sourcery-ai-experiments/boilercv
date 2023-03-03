"""Generate build information for the last version compiled in WSL."""

from pathlib import Path

import cv2 as cv

Path("build.txt").write_text(encoding="utf-8", data=cv.getBuildInformation())
