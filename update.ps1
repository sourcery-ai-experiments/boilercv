$VENV_ACTIVATE_WINDOWS = '.venv/Scripts/activate'
$VENV_ACTIVATE_UNIX = '.venv/bin/Activate.ps1'

if ( Test-Path $VENV_ACTIVATE_WINDOWS ) { . $VENV_ACTIVATE_WINDOWS }
elseif ( Test-Path $VENV_ACTIVATE_UNIX ) { . $VENV_ACTIVATE_UNIX }
else {
    throw [System.Management.Automation.ItemNotFoundException] 'Could not find a virtual environment.'
}
python -m pip install -U pip  # instructed to do this by pip
pip install -U setuptools wheel  # must be done separately from above
pip install -U -r .tools/requirements/requirements_dev.txt
pip uninstall -y boilercv
python .tools/scripts/bump_pyproject.py
pip install -e .

# If we are in WSL, replace required OpenCV with the debug build
$OPENCV_DEBUG_BUILD = '/home/user/opencv-python/dist/opencv_contrib_python-4.6.0.66-cp310-cp310-linux_x86_64.whl'
if ( Test-Path $OPENCV_DEBUG_BUILD ) { pip install --force-reinstall $OPENCV_DEBUG_BUILD }
