<#.SYNOPSIS
Synchronize Python dependencies.
#>

Param(
    # Python version.
    [string]$Version = (Get-Content '.copier-answers.yml' |
            Select-String -Pattern '^python_version:\s?["'']([^"'']*)["'']$').Matches.Groups[1].value,
    # Sync to highest pinned dependencies.
    [switch]$Highest,
    # Combine lockfiles if in CI.
    [switch]$Combine
)

# * -------------------------------------------------------------------------------- * #
# * Configuration

# ? Despite being default since 7.4, this needs to be explicit for some GHA runners
$PSNativeCommandUseErrorActionPreference = $true
$PSNativeCommandUseErrorActionPreference | Out-Null

# * -------------------------------------------------------------------------------- * #
# * Constants

$RE_VERSION = $([Regex]::Escape($Version))
$VENV = '.venv'
# ? Command modifier for `uv` if running in CI.
$UV_MOD = $Env:CI ? '--system --break-system-packages' : ''
# ? CLI flag for highest pinned dependencies.
# ? $PY is a CI-aware Python interpreter defined later but usable in Initialize-Python

# * -------------------------------------------------------------------------------- * #
# * Main inner function, invoked at the end of this script

function Sync-Python {
    <#.SYNOPSIS
    Synchronize Python dependencies.
    #>
    Initialize-PythonEnv
    Sync-PythonEnv
}

# * -------------------------------------------------------------------------------- * #
# * CI-aware jobs

function Initialize-PythonEnv {
    <#.SYNOPSIS
    Bootstrap the environment.
    #>
    install-uv
    install '-e .tools/.'
    if ($Env:CI) {
        run "copier update --defaults --vcs-ref $(git rev-parse HEAD:submodules/template)"
        # ? Install `uv` again in case it changed after `copier update`.
        install-uv
    }
    tools 'sync-paired-deps'
}

function Sync-PythonEnv {
    <#.SYNOPSIS
    Synchronize Python environment.
    #>
    if ($Env:CI) {
        if ($Combine) {
            tools 'combine-locks'
            return Get-Lockfile | sync
        }
        else {
            tools 'lock'
            tools 'lock --highest'
            return
        }
    }
    return Get-Lockfile -Create | sync
}

function Get-Lockfile {
    <#.SYNOPSIS
    Get lockfile.
    #>
    Param(
        # Attempt to populate the lockfile with an existing lock.
        [switch]$Create
    )
    return tools "get-lockfile $(Get-Flag 'highest' $Highest) $(Get-Flag 'create' $Create)"
}

function Get-Flag {
    <#.SYNOPSIS
    Get flag suitable for passing to CLI expecting flags like `--flag` and `--no-flag`.
    #>
    Param(
        # Flag.
        [Parameter(Mandatory, ValueFromPipeline)][string]$Flag,
        # Enabled.
        [bool]$Enable
    )
    return "--$($Enable ? '' : 'no-')$Flag"
}

# * -------------------------------------------------------------------------------- * #
# * Shorthand functions for common operations which depend on $PY and Get-Python

function run {
    <#.SYNOPSIS
    Invoke a Python module.
    #>
    Param([Parameter(Mandatory, ValueFromPipeline)][string]$String)
    Invoke-Expression "$Py -m $String"
}

function install-uv {
    <#.SYNOPSIS
    Install uv.
    #>
    run "pip install $(Get-Content '.tools/requirements/uv.in')"
}

function install {
    <#.SYNOPSIS
    CI-aware run of `uv pip install`.
    #>
    Param([Parameter(Mandatory, ValueFromPipeline)][string]$String)
    run "uv pip install $UV_MOD $String"
}

function sync {
    <#.SYNOPSIS
    CI-aware run of `uv pip sync`.
    #>
    Param([Parameter(Mandatory, ValueFromPipeline)][string]$String)
    run "uv pip sync $UV_MOD $String"
}

function tools {
    <#.SYNOPSIS
    Run `boilercv_tools` commands.
    #>
    Param([Parameter(Mandatory, ValueFromPipeline)][string]$String)
    run "boilercv_tools $String"
}

# * -------------------------------------------------------------------------------- * #
# * Get the CI-aware Python interpreter and call this script's main function

function Get-Python {
    <#.SYNOPSIS
    Get Python interpreter, global in CI, or activated virtual environment locally.
    #>
    $GlobalPy = Get-GlobalPython
    if ($Env:CI) {
        return $GlobalPy
    }
    if (! (Test-Path $VENV)) {
        if (! $GlobalPy) {
            throw "Expected Python $Version, which does not appear to be installed. Ensure it is installed (e.g. from https://www.python.org/downloads/) and run this script again."
        }
        Invoke-Expression "$GlobalPy -m venv $VENV"
    }
    $VenvPy = Start-PythonEnv $VENV
    $foundVersion = Invoke-Expression "$VenvPy --version"
    if (! ($foundVersion |
                Select-String -Pattern "^Python $RE_VERSION\.\d*$")) {
        throw "Found virtual environment with Python version $foundVersion. Expected $Version. Remove the virtual environment and run this script again to recreate."
    }
    return $VenvPy
}

function Get-GlobalPython {
    <#.SYNOPSIS
    Get global Python interpreter.
    #>
    if (Test-Command 'py') {
        if (py --list | Select-String -Pattern "^\s?-V:$RE_VERSION") {
            return "py -$Version"
        }
    }
    elseif (Test-Command "python$Version") {
        return "python$Version"
    }
    elseif (Test-Command 'python') {
        Write-Warning "Attempting to invoke Python $Version from 'python' alias."
        return 'python'
    }
    Write-Warning "Python $Version does not appear to be installed. Download and install from 'https://www.python.org/downloads/'."
    return
}

function Start-PythonEnv {
    <#.SYNOPSIS
    Activate and get the Python interpreter for the virtual environment.
    #>
    if ($IsWindows) {
        $bin = 'Scripts'
        $py = 'python.exe'
    }
    else {
        $bin = 'bin'
        $py = 'python'
    }
    . "$VENV/$bin/activate"
    return "$Env:VIRTUAL_ENV/Scripts/$py"

}

function Test-Command {
    <#.SYNOPSIS
    Like `Get-Command` but errors are ignored.
    #>
    return Get-Command @args -ErrorAction Ignore
}

# ? CI-aware Python interpreter and invocation of the main function
$PY = Get-Python
Sync-Python
