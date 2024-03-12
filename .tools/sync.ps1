<#.SYNOPSIS
Synchronize the Python environment with this project's locked dependencies.
#>

Param(
    # Python version to install or expect.
    [string]$Version = (Get-Content '.copier-answers.yml' |
            Select-String -Pattern '^python_version:\s?["'']([^"'']*)["'']$').Matches.Groups[1].value
)

function Main {
    <#.SYNOPSIS
    Runs when this script is invoked.
    #>
    $lock = '.lock'
    $Py = Get-Python
    Invoke-Expression "$Py -m pip install uv"
    if ($Env:CI) {
        $ErrorActionPreference = 'Stop'
        pwsh --version
        $Env:CI
        $Env:LOCK
        $Env:TESTP
        $Env:COMBINE
        Invoke-Expression "$Py -m uv pip install --system --break-system-packages -e .tools/."
        Invoke-Expression "$Py -m copier update --defaults --vcs-ref $(git rev-parse HEAD:submodules/template)"
        Invoke-Expression "$Py -m boilercv_tools sync"
        if ($Env:LOCK) {
            Invoke-Expression "$Py -m boilercv_tools lock"
            Invoke-Expression "$Py -m uv pip sync --system --break-system-packages $(Get-ChildItem $lock)"
            Invoke-Expression "$Py -m boilercv_tools lock --highest"
        }
        if ($Env:TEST) { Invoke-Expression "$Py -m pytest" }
        elseif ($Env:COMBINE) {
            Invoke-Expression "$Py -m boilercv_tools combine-locks"
        }
        return
    }
    Invoke-Expression "$Py -m uv pip install -e .tools/."
    if (Test-Path $lock) { Remove-Item -Recurse $lock }
    Invoke-Expression "$Py -m boilercv_tools get-lock"
    Invoke-Expression "$Py -m uv pip sync $(Get-ChildItem $lock)"
}

function Get-Python {
    <#.SYNOPSIS
    Get Python environment for this project.
    #>
    $globalPy = Get-GlobalPython
    if ($Env:CI) {
        return $globalPy
    }
    $venv = '.venv'
    if (! (Test-Path $venv)) {
        if (! $globalPy) {
            throw "Expected Python $Version, which does not appear to be installed. Ensure it is installed (e.g. from https://www.python.org/downloads/) and run this script again."
        }
        Invoke-Expression "$globalPy -m venv $Py"
    }
    $Py = Start-PythonEnv $venv
    $foundVersion = Invoke-Expression "$Py --version"
    if (! ($foundVersion |
                Select-String -Pattern "^Python $([Regex]::Escape($Version))\.\d*$")) {
        throw "Found virtual environment with Python version $foundVersion. Expected $Version. Remove the virtual environment and run this script again to recreate."
    }
    return $Py
}

function Get-GlobalPython {
    <#.SYNOPSIS
    Get the global Python interpreter for a certain Python version.
    #>
    if (Get-Command 'py' -ErrorAction Ignore) {
        if (py --list | Select-String -Pattern "^\s?-V:$([Regex]::Escape($Version))") {
            return "py -$Version"
        }
    }
    elseif (Get-Command "python$Version" -ErrorAction Ignore) {
        return "python$Version"
    }
    Write-Warning "Python $Version does not appear to be installed. Download and install from 'https://www.python.org/downloads/'."
    return
}

function Start-PythonEnv {
    <#.SYNOPSIS
    Activate a Python virtual environment and return its interpreter.
    #>
    Param(
        # Virtual environment name to activate.
        [Parameter(Mandatory, ValueFromPipeline)][string]$Name = '.venv'
    )
    if ($IsWindows) {
        . "$Name/Scripts/activate"
        return "$Env:VIRTUAL_ENV/Scripts/python.exe"
    }
    else {
        . "$Name/bin/activate"
        return "$Env:VIRTUAL_ENV/bin/python"
    }
}

Main
