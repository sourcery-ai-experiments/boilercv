<#.SYNOPSIS
Sync Python dependencies.#>
Param(
    # Python version.
    [Parameter(ValueFromPipeline)][string]$Version = (Get-Content '.copier-answers.yml' | Select-String -Pattern '^python_version:\s?["'']([^"'']+)["'']$').Matches.Groups[1].value,
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
    # Don't use global Python in CI.
    [switch]$NoGlobalInCI
)

. 'scripts/Set-StrictErrors.ps1'

# * -------------------------------------------------------------------------------- * #
# * Main function, invoked at the end of this script and has the context of all below

function Sync-Python {
    <#.SYNOPSIS
    Sync Python dependencies.#>

    '*** LOCKING/SYNCING' | Write-Progress

    'INSTALLING UV' | Write-Progress
    Install-Uv

    'INSTALLING TOOLS' | Write-Progress
    Invoke-UvPip Install '-e tools/.'

    'SYNCING PAIRED DEPENDENCIES' | Write-Progress
    Invoke-Tools 'sync-paired-deps'

    if ($Env:CI -and !$NoCopy) {
        'UPDATING FROM TEMPLATE' | Write-Progress
        $head = git rev-parse HEAD:submodules/template
        Invoke-PythonModule "copier update --defaults --vcs-ref $head"
    }
    if ($Lock) {
        'LOCKING' | Write-Progress
        'Dev', 'Low', 'High' | Invoke-Lock
        'LOCKED' | Write-Progress -Done
    }
    if ($Lock -or $Merge) {
        'MERGING LOCKS' | Write-Progress; Invoke-Tools 'merge-locks'
    }
    if (!$NoSync) {
        'SYNCING' | Write-Progress
        Get-Lock $Sync | Invoke-UvPip Sync
        'SYNCED' | Write-Progress -Done
    }
    if (!$Env:CI -and !$NoHooks) {
        'INSTALLING PRE-COMMIT HOOKS' | Write-Progress
        Invoke-PythonScript 'pre-commit' 'install'
        'commit-msg', 'post-checkout', 'pre-commit', 'pre-merge-commit', 'pre-push' |
            Install-Hook
    }
    '...DONE ***' | Write-Progress -Done
}

function Write-Progress {
    <#.SYNOPSIS
    Write progress and completion messages.#>
    Param([Parameter(Mandatory, ValueFromPipeline)][string]$Message,
        [switch]$Done)
    begin { $Color = $Done ? 'Green' : 'Yellow' }
    process {
        Write-Host
        Write-Host "$Message$($Done ? '' : '...')" -ForegroundColor $Color
    }
}

function Install-Hook {
    <#.SYNOPSIS
    Install pre-commit hook.#>
    Param([Parameter(Mandatory, ValueFromPipeline)][string]$Hook)
    process {
        if (Test-Path ".git/hooks/$Hook") { return }
        Invoke-PythonScript 'pre-commit' "install-hooks --hook-type $Hook"
    }
}

function Install-Uv {
    <#.SYNOPSIS
    Install uv.#>
    Invoke-PythonModule "pip install $(Get-Content 'requirements/uv.in')"
}

function Invoke-UvPip {
    <#.SYNOPSIS
    CI-aware invocation of `uv pip`.#>
    Param([ArgumentCompletions('Install', 'Sync')][string]$Cmd,
        [Parameter(Mandatory, ValueFromPipeline)][string]$Arguments)
    process {
        $System = $Env:CI ? '--system --break-system-packages' : ''
        Invoke-PythonModule "uv pip $($Cmd.ToLower()) $System $Arguments"
    }
}

function Invoke-Lock {
    <#.SYNOPSIS
    Lock the environment.#>
    Param([Parameter(Mandatory, ValueFromPipeline)]
        [ArgumentCompletions('Dev', 'Low', 'High')][string]$Kind)
    process { return Invoke-Tools "lock $($Kind.ToLower())" }
}

function Get-Lock {
    <#.SYNOPSIS
    Retrieve a lock.#>
    Param([Parameter(Mandatory, ValueFromPipeline)][ArgumentCompletions('Dev', 'Low', 'High')][string]$Kind)
    process { return Invoke-Tools "get-lock $($Kind.ToLower())" }
}

function Invoke-Tools {
    <#.SYNOPSIS
    Run `boilercv_tools` commands.#>
    Param([Parameter(Mandatory, ValueFromPipeline)][string]$Arguments)
    process { Invoke-PythonModule "boilercv_tools $Arguments" }
}

function Invoke-PythonModule {
    <#.SYNOPSIS
    Invoke Python module.#>
    Param([Parameter(Mandatory, ValueFromPipeline)][string]$Arguments)
    process { Invoke-Expression "$PYTHON -m $Arguments" }
}

function Invoke-PythonScript {
    <#.SYNOPSIS
    Invoke Python script installed in the environment.#>
    Param([Parameter(Mandatory)][string]$Cmd,
        [Parameter(Mandatory, ValueFromPipeline)][string]$Arguments)
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
    Get Python interpreter, global in CI, or activated virtual environment locally.#>
    $GlobalPy = Get-GlobalPython
    if ($Env:CI -and !$NoGlobalInCI) {
        Write-Progress "USING GLOBAL PYTHON: $GlobalPy" -Done
        return $GlobalPy
    }
    if (!(Test-Path $VENV_PATH)) { Invoke-Expression "$GlobalPy -m venv $VENV_PATH" }
    $VenvPy = Start-PythonEnv $VENV_PATH
    Write-Progress "USING VIRTUAL ENVIRONMENT: $VenvPy" -Done
    $foundVersion = Invoke-Expression "$VenvPy --version"
    if ($foundVersion |
            Select-String -Pattern "^Python $RE_VERSION\.\d+$") { return $VenvPy }
    Write-Progress "REMOVING VIRTUAL ENVIRONMENT: $Env:VIRTUAL_ENV" -Done
    Remove-Item -Recurse -Force $Env:VIRTUAL_ENV
    return Get-Python
}

function Get-GlobalPython {
    <#.SYNOPSIS
    Get global Python interpreter.#>
    if ((Test-Command 'py') -and
        (py '--list' |
            Select-String -Pattern "^\s?-V:$RE_VERSION")) { return "py -$Version" }
    elseif (Test-Command "python$Version") { return "python$Version" }
    elseif (Test-Command 'python') { return 'python' }
    throw "Expected Python $Version, which does not appear to be installed. Ensure it is installed (e.g. from https://www.python.org/downloads/) and run this script again."
}

function Start-PythonEnv {
    <#.SYNOPSIS
    Activate and get the Python interpreter for the virtual environment.#>
    if ($IsWindows) { $bin = 'Scripts'; $python = 'python.exe' }
    else { $bin = 'bin'; $python = 'python' }
    Invoke-Expression "$VENV_PATH/$bin/Activate.ps1"
    return "$Env:VIRTUAL_ENV/$bin/$python"
}

function Test-Command {
    <#.SYNOPSIS
    Like `Get-Command` but errors are ignored.#>
    return Get-Command @args -ErrorAction 'Ignore'
}

# * -------------------------------------------------------------------------------- * #
# * CI-aware Python interpreter and invocation of the main function

$PYTHON = Get-Python
$SCRIPTS = Split-Path $PYTHON
Sync-Python
