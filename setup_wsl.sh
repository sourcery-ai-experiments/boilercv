python -m venv .venv --clear --upgrade-deps
.venv/bin/activate
pip install -U setuptools wheel  # must be done separately from above
pip install -U -r .tools/requirements/requirements_dev.txt
pip uninstall -y boilercv
pip install -e .
pip install --force-reinstall /home/user/opencv-python/dist/opencv_contrib_python-4.6.0.66-cp310-cp310-linux_x86_64.whl
