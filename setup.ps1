$GLOBAL_PYTHON = 'py -3.10'
try { . $GLOBAL_PYTHON --version } catch [System.Management.Automation.CommandNotFoundException] { $GLOBAL_PYTHON = 'python3.10' }
rm -rf .venv
. $GLOBAL_PYTHON -m venv .venv --upgrade-deps
. ./update.ps1
pre-commit install
pre-commit
