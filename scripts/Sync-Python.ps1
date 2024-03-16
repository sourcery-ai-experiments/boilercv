<#.SYNOPSIS
Sync Python dependencies.#>
Param(
    # Python version.
    [Parameter(ValueFromPipeline)][string]$Version = (Get-Content '.copier-answers.yml' | Select-String -Pattern '^python_version:\s?["'']([^"'']+)["'']$').Matches.Groups[1].value,
    # Sync to highest dependencies
    [switch]$High,
    # Recompile dependencies
    [switch]$Recompile,
    # Add all local dependency compilations to the lock.
    [switch]$Lock,
    # Optionally skip syncing, if just recompiling or locking.
    [switch]$NoSync,
    # Don't recopy the template.
    [switch]$NoCopy,
    # Use virtual environment even in CI.
    [switch]$VenvInCI
)

. 'scripts/Set-StrictErrors.ps1'

function Sync-Python {
    <#.SYNOPSIS
    Sync Python dependencies.#>
    $py = Get-Python
    '*** SYNCING' | Write-Progress
    'SYNCING SUBMODULES' | Write-Progress
    git submodule update --init --merge
    'SUBMODULES SYNCED' | Write-Progress -Done
    'INSTALLING UV' | Write-Progress
    Invoke-Expression "$py -m pip install $(Get-Content 'requirements/uv.in')"
    'INSTALLING TOOLS' | Write-Progress
    $System = $Env:CI ? '--system --break-system-packages' : ''
    Invoke-Expression "$py -m uv pip install $System --editable tools/."
    if (!$Env:CI) {
        'SYNCING LOCAL DEV CONFIGS' | Write-Progress
        Invoke-Expression "$py -m boilercv_tools sync-local-dev-configs"
        'LOCAL DEV CONFIGS SYNCED' | Write-Progress -Done
        'INSTALLING PRE-COMMIT HOOKS' | Write-Progress
        Invoke-Expression "$(Split-Path $py)/pre-commit install --install-hooks --hook-type pre-commit --hook-type pre-push --hook-type commit-msg --hook-type post-checkout --hook-type pre-merge-commit"
    }
    if ($Env:CI -and !$NoCopy) {
        'SYNCING PROJECT WITH TEMPLATE' | Write-Progress
        $head = git rev-parse HEAD:submodules/template
        Invoke-Expression "$py -m copier update --defaults --vcs-ref $head"
    }
    if ($Recompile) {
        'RECOMPILING' | Write-Progress
        Invoke-Expression "$py -m boilercv_tools recompile"
        Invoke-Expression "$py -m boilercv_tools recompile --high"
        'COMPILED' | Write-Progress -Done
    }
    if ($Recompile -or $Lock) {
        'LOCKING' | Write-Progress
        Invoke-Expression "$py -m boilercv_tools lock"
    }
    if (!$NoSync) {
        'SYNCING' | Write-Progress
        $compilation = Invoke-Expression "$py -m boilercv_tools compile --high=$($High.ToLower())"
        Invoke-Expression "$py -m uv pip sync $System $compilation"
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
        if (!$Done) { Write-Host }
        Write-Host "$Message$($Done ? '' : '...')" -ForegroundColor $Color
    }
}

# ? For regex comparisons
$RE_VERSION = $([Regex]::Escape($Version))
# ? Virtual environment path
$VENV_PATH = '.venv'

function Get-Python {
    <#.SYNOPSIS
    Get Python interpreter, global in CI, or activated virtual environment locally.#>
    $GlobalPy = Get-GlobalPython
    if ($Env:CI -and !$VenvInCI) {
        Write-Progress "USING GLOBAL PYTHON: $GlobalPy" -Done
        return $GlobalPy
    }
    if (!(Test-Path $VENV_PATH)) { Invoke-Expression "$GlobalPy -m venv $VENV_PATH" }
    $VenvPy = Start-PythonEnv $VENV_PATH
    Write-Progress "USING VIRTUAL ENVIRONMENT: $VenvPy" -Done
    $foundVersion = Invoke-Expression "$VenvPy --version"
    if ($foundVersion |
            Select-String -Pattern "^Python $RE_VERSION\.\d+$") {
        return $VenvPy
    }
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
    if ($IsWindows) { $bin = 'Scripts'; $py = 'python.exe' }
    else { $bin = 'bin'; $py = 'python' }
    Invoke-Expression "$VENV_PATH/$bin/Activate.ps1"
    return "$Env:VIRTUAL_ENV/$bin/$py"
}

function Test-Command {
    <#.SYNOPSIS
    Like `Get-Command` but errors are ignored.#>
    return Get-Command @args -ErrorAction 'Ignore'
}

Sync-Python
