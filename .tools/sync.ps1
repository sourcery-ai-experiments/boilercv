<#.SYNOPSIS
Synchronize the Python environment with this project's locked dependencies.
#>

Param(
    # Python version to install or expect.
    [string]$Version = (Get-Content '.copier-answers.yml' |
            Select-String -Pattern '^python_version:\s?["'']([^"'']*)["'']$').Matches.Groups[1].value
)

$PSNativeCommandUseErrorActionPreference = $true
$PSNativeCommandUseErrorActionPreference | Out-Null

function Start-PythonEnv {
    <#.SYNOPSIS
    Activate a Python virtual environment and return its interpreter.
    #>
    Param(
        # Virtual environment name to activate.
        [Parameter(ValueFromPipeline)][string]$Name = '.venv'
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

$Py = Get-Python

function run {
    Param([Parameter(Mandatory, ValueFromPipeline)][string]$String)
    Invoke-Expression "$Py -m $String"
}

function inst {
    Param([Parameter(Mandatory, ValueFromPipeline)][string]$String)
    if ($Env:CI) {
        run "uv pip install --system --break-system-packages $String"
    }
    else {
        run "uv pip install $String"
    }
}

function sync {
    Param([Parameter(Mandatory, ValueFromPipeline)][string]$String)
    if ($Env:CI) {
        run "uv pip sync  --system --break-system-packages $String"
    }
    else {
        run "uv pip sync $String"
    }
}

function tools {
    Param([Parameter(Mandatory, ValueFromPipeline)][string]$String)
    run "boilercv_tools $String"
}

function SETUP {
    run 'pip install uv'
    inst '-e .tools/.'
    run "$tools find-lock"
    sync $lock
}

function CI_ONLY_SETUP {
    run "copier update --defaults --vcs-ref $(git rev-parse HEAD:submodules/template)"
    run "$tools sync"
}

function LOCK {
    $lock = tools 'get-lockfile'
    run "$tools lock"
    sync $lock
    run "$tools lock --highest"
    elseif ($Env:TEST) {
        run 'pytest'
    }
}

function TEST {
    run 'pytest'
}

# * -------------------------------------------------------------------------------- * #

function COMBINE {
    tools 'combine-locks'
    run "$tools sync"
    run "$tools combine-locks"
}
