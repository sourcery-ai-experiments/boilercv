<#.SYNOPSIS
Sync Python dependencies.
#>

Param(
    # Python version.
    [Parameter(ValueFromPipeline)][string]$Version = (Get-Content '.copier-answers.yml' |
            Select-String -Pattern '^python_version:\s?["'']([^"'']*)["'']$').Matches.Groups[1].value,
    # Kind of lock to sync the Python environment with.
    [ArgumentCompletions('None', 'Dev', 'Low', 'High')][string]$Sync = 'Dev',
    # Lock the environment.
    [switch]$Lock,
    # Merge existing locks.
    [switch]$Merge,
    # Toggle CI to behave as local and vice versa. Local runs still always use `.venv`.
    [switch]$ToggleCI,
    # Force `.venv` even in CI. Local runs still always use `.venv`.
    [switch]$ForceVenv,
    # Skip template recopying.
    [switch]$SkipCopy,
    # Skip pre-commit hooks.
    [switch]$SkipHooks
)

. '.tools/scripts/Set-StrictErrors.ps1'

# * -------------------------------------------------------------------------------- * #
# * Main function, invoked at the end of this script and has the context of all below

function Sync-Python {
    <#.SYNOPSIS
    Sync Python dependencies.
    #>
    Write-Progress '*** LOCKING/SYNCING...'
    $CI = $Env:CI -xor $ToggleCI
    if ($CI) { Write-Progress 'BEHAVING AS IF IN CI' -Done }
    Write-Progress 'INSTALLING UV'
    Install-Uv
    Write-Progress 'INSTALLING TOOLS'
    Invoke-UvPip Install '-e .tools/.'
    Write-Progress 'SYNCING PAIRED DEPENDENCIES'
    Invoke-Tools 'sync-paired-deps'
    if ($CI -and (! $SkipCopy)) {
        Write-Progress 'UPDATING FROM TEMPLATE...'
        $head = git rev-parse HEAD:submodules/template
        Invoke-PythonModule "copier update --defaults --vcs-ref $head"
        # ? Install `uv` again in case it changed after `copier update`.
        Install-Uv
    }
    if ($Lock) {
        Write-Progress 'LOCKING...'
        if ($CI) { 'Dev', 'Low', 'High' | Invoke-Lock }
        else { Invoke-Lock $Sync }
        Write-Progress 'LOCKED' -Done
    }
    if ($Merge) {
        Write-Progress 'MERGING LOCKS'
        Invoke-Tools 'merge-locks'
        Write-Progress 'MERGED'
    }
    if ($Sync -ne 'None') {
        Write-Progress 'SYNCING'
        Get-Lock $Sync | Invoke-UvPip Sync
    }
    if (! ($CI -or $SkipHooks)) {
        Write-Progress 'INSTALLING PRE-COMMIT HOOKS'
        $h = '--hook-type'
        $HookTypes = @(
            $h, 'commit-msg'
            $h, 'post-checkout'
            $h, 'pre-commit'
            $h, 'pre-merge-commit'
            $h, 'pre-push'
        )
        pre-commit install --install-hooks @HookTypes
    }
    Write-Progress '...DONE ***' -Done
}

function Write-Progress {
    <#.SYNOPSIS
    Write a message in green.
    #>
    Param(
        [Parameter(Mandatory, ValueFromPipeline)][string]$Message,
        [switch]$Done
    )
    Write-Host
    Write-Host $Message -ForegroundColor $($Done ? 'Green' : 'Yellow')

}


# * -------------------------------------------------------------------------------- * #
# * Shorthand functions for common operations which depend on $PY and Get-Python

function Install-Uv {
    <#.SYNOPSIS
    Install uv.
    #>
    Invoke-PythonModule "pip install $(Get-Content '.tools/requirements/uv.in')"
}

function Invoke-UvPip {
    <#.SYNOPSIS
    CI-aware invocation of `uv pip`.
    #>
    Param(
        [ArgumentCompletions('Install', 'Sync')][string]$Cmd,
        [Parameter(Mandatory, ValueFromPipeline)][string]$Arguments
    )
    $System = $CI ? '--system --break-system-packages' : ''
    Invoke-PythonModule "uv pip $($Cmd.ToLower()) $System $Arguments"
}

function Invoke-Tools {
    <#.SYNOPSIS
    Run `boilercv_tools` commands.
    #>
    Param([Parameter(Mandatory, ValueFromPipeline)][string]$Arguments)
    Invoke-PythonModule "boilercv_tools $Arguments"
}

function Invoke-Lock {
    <#.SYNOPSIS
    Lock the environment.
    #>
    Param(
        # Kind of lock.
        [Parameter(Mandatory, ValueFromPipeline)][ArgumentCompletions('Dev', 'Low', 'High')][string]$Kind
    )
    return Invoke-Tools "lock $($Kind.ToLower())"
}

function Get-Lock {
    <#.SYNOPSIS
    Get lockfile.
    #>
    Param(
        # Kind of lock.
        [Parameter(Mandatory, ValueFromPipeline)][ArgumentCompletions('Dev', 'Low', 'High')][string]$Kind
    )
    return Invoke-Tools "get-lock $($Kind.ToLower())"
}


function Invoke-PythonModule {
    <#.SYNOPSIS
    Invoke a Python module.
    #>
    Param([Parameter(Mandatory, ValueFromPipeline)][string]$Arguments)
    Invoke-Expression "$Py -m $Arguments"
}


# * -------------------------------------------------------------------------------- * #
# * Get the CI-aware Python interpreter and call this script's main function

# ? For regex comparisons
$RE_VERSION = $([Regex]::Escape($Version))
# ? Virtual environment path
$VENV_PATH = '.venv'

function Get-Python {
    <#.SYNOPSIS
    Get Python interpreter, global in CI, or activated virtual environment locally.
    #>
    $GlobalPy = Get-GlobalPython
    # ? Use `$Env:CI` here instead of `$CI` to enforce `.venv` locally
    if ($Env:CI -and (! $ForceVenv)) {
        return $GlobalPy
    }
    if (! (Test-Path $VENV_PATH)) {
        if (! $GlobalPy) {
            throw "Expected Python $Version, which does not appear to be installed. Ensure it is installed (e.g. from https://www.python.org/downloads/) and run this script again."
        }
        Invoke-Expression "$GlobalPy -m venv $VENV_PATH"
    }
    $VenvPy = Start-PythonEnv $VENV_PATH
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
    Invoke-Expression "$VENV_PATH/$bin/Activate.ps1"
    return "$Env:VIRTUAL_ENV/$bin/$py"
}

function Test-Command {
    <#.SYNOPSIS
    Like `Get-Command` but errors are ignored.
    #>
    return Get-Command @args -ErrorAction Ignore
}

# * -------------------------------------------------------------------------------- * #
# * CI-aware Python interpreter and invocation of the main function

$PY = Get-Python
Sync-Python
