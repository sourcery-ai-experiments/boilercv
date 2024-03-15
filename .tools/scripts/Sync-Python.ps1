<#.SYNOPSIS
Sync Python dependencies.
#>

Param(
    # Python version.
    [Parameter(ValueFromPipeline)][string]$Version = (Get-Content '.copier-answers.yml' | Select-String -Pattern '^python_version:\s?["'']([^"'']*)["'']$').Matches.Groups[1].value,
    # Lock the environment.
    [switch]$Lock,
    # Merge existing locks.
    [switch]$Merge,
    # Kind of lock to sync the Python environment with.
    [ArgumentCompletions('Dev', 'Low', 'High')][string]$Sync = 'Dev',
    # Don't sync.
    [switch]$NoSync,
    # Don't recopy the template.
    [switch]$NoCopy,
    # Don't install pre-commit hooks.
    [switch]$NoHooks,
    # Toggle CI to behave as local and vice versa. Local runs still always use `.venv`.
    [switch]$ToggleCI,
    # Don't use global Python in CI. Local runs still always use `.venv`.
    [switch]$NoGlobalInCI
)

. '.tools/scripts/Set-StrictErrors.ps1'
$ActuallyInCI = $Env:CI
$CI = $ActuallyInCI -xor $ToggleCI

# * -------------------------------------------------------------------------------- * #
# * Main function, invoked at the end of this script and has the context of all below

function Sync-Python {
    <#.SYNOPSIS
    Sync Python dependencies.
    #>

    '*** LOCKING/SYNCING' | Write-Progress
    if (!$ActuallyInCI -and $CI) { 'BEHAVING AS IF IN CI' | Write-Progress -Done }

    'INSTALLING UV' | Write-Progress
    Install-Uv

    'INSTALLING TOOLS' | Write-Progress
    Invoke-UvPip Install '-e .tools/.'

    'SYNCING PAIRED DEPENDENCIES' | Write-Progress
    Invoke-Tools 'sync-paired-deps'

    if ($CI -and !$NoCopy) {
        'UPDATING FROM TEMPLATE' | Write-Progress
        $head = git rev-parse HEAD:submodules/template
        Invoke-PythonModule "copier update --defaults --vcs-ref $head"
        # ? Install `uv` again in case it changed after `copier update`.
        Install-Uv
    }
    if ($Lock) {
        'LOCKING' | Write-Progress
        'Dev', 'Low', 'High' | Invoke-Lock
        'LOCKED' | Write-Progress -Done
    }
    if ($Lock -or $Merge) {
        'MERGING LOCKS' | Write-Progress
        Invoke-Tools 'merge-locks'
    }
    if (!$NoSync) {
        'SYNCING' | Write-Progress
        Get-Lock $Sync | Invoke-UvPip Sync
        'SYNCED' | Write-Progress -Done
    }
    if (!$CI -and !$NoHooks) {
        'INSTALLING PRE-COMMIT HOOKS' | Write-Progress
        Invoke-PythonScript 'pre-commit' 'install --install-hooks --hook-type commit-msg --hook-type post-checkout --hook-type pre-commit --hook-type pre-merge-commit --hook-type pre-push'
    }
    '...DONE ***' | Write-Progress -Done
}

function Write-Progress {
    <#.SYNOPSIS
    Write a message in green.
    #>
    Param(
        [Parameter(Mandatory, ValueFromPipeline)][string]$Message,
        [switch]$Done
    )
    begin {
        $Color = $Done ? 'Green' : 'Yellow'
    }
    process {
        Write-Host
        Write-Host "$Message$($Done ? '' : '...')" -ForegroundColor $Color
    }
}

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
    process {
        $System = $ActuallyInCI ? '--system --break-system-packages' : ''
        Invoke-PythonModule "uv pip $($Cmd.ToLower()) $System $Arguments"
    }
}

function Invoke-Tools {
    <#.SYNOPSIS
    Run `boilercv_tools` commands.
    #>
    Param([Parameter(Mandatory, ValueFromPipeline)][string]$Arguments)
    process { Invoke-PythonModule "boilercv_tools $Arguments" }
}

function Invoke-Lock {
    <#.SYNOPSIS
    Lock the environment.
    #>
    Param(
        # Kind of lock.
        [Parameter(Mandatory, ValueFromPipeline)][ArgumentCompletions('Dev', 'Low', 'High')][string]$Kind
    )
    process { return Invoke-Tools "lock $($Kind.ToLower())" }
}

function Get-Lock {
    <#.SYNOPSIS
    Get lockfile.
    #>
    Param(
        # Kind of lock.
        [Parameter(Mandatory, ValueFromPipeline)][ArgumentCompletions('Dev', 'Low', 'High')][string]$Kind
    )
    process { return Invoke-Tools "get-lock $($Kind.ToLower())" }
}

function Invoke-PythonModule {
    <#.SYNOPSIS
    Invoke a Python module.
    #>
    Param([Parameter(Mandatory, ValueFromPipeline)][string]$Arguments)
    process { Invoke-Expression "$PYTHON -m $Arguments" }
}

function Invoke-PythonScript {
    <#.SYNOPSIS
    Invoke Python scripts.
    #>
    Param(
        [Parameter(Mandatory)][string]$Cmd,
        [Parameter(Mandatory, ValueFromPipeline)][string]$Arguments
    )
    process { Invoke-Expression "$SCRIPTS/$Cmd $Arguments" }
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
    if ($ActuallyInCI -and $CI -and !$NoGlobalInCI) {
        Write-Progress "USING GLOBAL PYTHON: $GlobalPy" -Done
        return $GlobalPy
    }
    if (!(Test-Path $VENV_PATH)) {
        if (!$GlobalPy) {
            throw "Expected Python $Version, which does not appear to be installed. Ensure it is installed (e.g. from https://www.python.org/downloads/) and run this script again."
        }
        Invoke-Expression "$GlobalPy -m venv $VENV_PATH"
    }
    $VenvPy = Start-PythonEnv $VENV_PATH
    Write-Progress "USING VIRTUAL ENVIRONMENT: $VenvPy" -Done
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
