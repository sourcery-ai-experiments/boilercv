<#.SYNOPSIS
Sync Python dependencies.
#>

Param(
    # Python version.
    [Parameter(ValueFromPipeline)][string]$Version = (Get-Content '.copier-answers.yml' | Select-String -Pattern '^python_version:\s?["'']([^"'']*)["'']$').Matches.Groups[1].value,
    # Kind of lock to sync the Python environment with.
    [ArgumentCompletions('Dev', 'Low', 'High')][string]$Sync = 'Dev',
    # Lock the environment.
    [switch]$Lock,
    # Merge existing locks.
    [switch]$Merge,
    # Don't sync.
    [switch]$NoSync,
    # Don't use global Python in CI. Local runs still always use `.venv`.
    [switch]$NoGlobalInCI,
    # Toggle CI to behave as local and vice versa. Local runs still always use `.venv`.
    [switch]$ToggleCI,
    # Don't recopy the template.
    [switch]$NoCopy,
    # Don't install pre-commit hooks.
    [switch]$NoHooks
)

. '.tools/scripts/Set-StrictErrors.ps1'

Write-Progress '*** LOCKING/SYNCING...'
$ActuallyInCI = $Env:CI
$CI = $ActuallyInCI -xor $ToggleCI
if (!$ActuallyInCI -and $CI) { Write-Progress 'BEHAVING AS IF IN CI' -Done }

# * -------------------------------------------------------------------------------- * #
# * Main function, invoked at the end of this script and has the context of all below

function Sync-Python {
    <#.SYNOPSIS
    Sync Python dependencies.
    #>
    Write-Progress 'INSTALLING UV'
    Install-Uv
    Write-Progress 'INSTALLING TOOLS'
    Invoke-UvPip Install '-e .tools/.'
    Write-Progress 'SYNCING PAIRED DEPENDENCIES'
    Invoke-Tools 'sync-paired-deps'
    if ($CI -and !$NoCopy) {
        Write-Progress 'UPDATING FROM TEMPLATE...'
        $head = git rev-parse HEAD:submodules/template
        Invoke-PythonModule "copier update --defaults --vcs-ref $head"
        # ? Install `uv` again in case it changed after `copier update`.
        Install-Uv
    }
    if ($Lock) {
        Write-Progress 'LOCKING...'
        'Dev', 'Low', 'High' | Invoke-Lock
        Write-Progress 'LOCKED' -Done
    }
    if ($Merge) {
        Write-Progress 'MERGING LOCKS'
        Invoke-Tools 'merge-locks'
        Write-Progress 'MERGED'
    }
    if (!$NoSync) {
        Write-Progress 'SYNCING'
        Get-Lock $Sync | Invoke-UvPip Sync
    }
    if (!$CI -and !$NoHooks) {
        Write-Progress 'INSTALLING PRE-COMMIT HOOKS'
        Invoke-PythonScript 'pre-commit' 'install --install-hooks --hook-type commit-msg --hook-type post-checkout --hook-type pre-commit --hook-type pre-merge-commit --hook-type pre-push'
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
# * Shorthand functions for common operations which depend on $PYTHON and Get-Python

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
    $System = $ActuallyInCI ? '--system --break-system-packages' : ''
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
    Invoke-Expression "$PYTHON -m $Arguments"
}

function Invoke-UvPip {
    <#.SYNOPSIS
    CI-aware invocation of `uv pip`.
    #>
    Param(
        [string]$Cmd,
        [Parameter(Mandatory, ValueFromPipeline)][string]$Arguments
    )
    Invoke-PythonModule "uv pip $($Cmd.ToLower()) $System $Arguments"
}

function Invoke-PythonScript {
    <#.SYNOPSIS
    Invoke Python scripts.
    #>
    Param(
        [string]$Cmd,
        [Parameter(Mandatory, ValueFromPipeline)][string]$Arguments
    )
    Invoke-Expression "$SCRIPTS/$Cmd $Arguments"
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
    Write-Progress "GLOBAL PYTHON: $GlobalPy" -Done
    if ($ActuallyInCI -and $CI -and !$NoGlobalInCI) {
        Write-Progress 'USING GLOBAL PYTHON' -Done
        return $GlobalPy
    }
    if (!(Test-Path $VENV_PATH)) {
        Write-Progress 'CREATING VIRTUAL ENVIRONMENT...'
        if (!$GlobalPy) {
            throw "Expected Python $Version, which does not appear to be installed. Ensure it is installed (e.g. from https://www.python.org/downloads/) and run this script again."
        }
        Invoke-Expression "$GlobalPy -m venv $VENV_PATH"
    }
    $VenvPy = Start-PythonEnv $VENV_PATH
    Write-Progress "USING VIRTUAL ENVIRONMENT = $VenvPy" -Done
    $foundVersion = Invoke-Expression "$VenvPy --version"
    if (!($foundVersion | Select-String -Pattern "^Python $RE_VERSION\.\d*$")) {
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
        $python = 'python.exe'
    }
    else {
        $bin = 'bin'
        $python = 'python'
    }
    Invoke-Expression "$VENV_PATH/$bin/Activate.ps1"
    return "$Env:VIRTUAL_ENV/$bin/$python"
}

function Test-Command {
    <#.SYNOPSIS
    Like `Get-Command` but errors are ignored.
    #>
    return Get-Command @args -ErrorAction Ignore
}

# * -------------------------------------------------------------------------------- * #
# * CI-aware Python interpreter and invocation of the main function

$PYTHON = Get-Python
$SCRIPTS = Split-Path $PYTHON
Sync-Python
