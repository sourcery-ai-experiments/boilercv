"""Generate build information for the last version compiled in WSL."""

from pathlib import Path

from cv2 import getBuildInformation

Path("build.txt").write_text(encoding="utf-8", data=getBuildInformation())
