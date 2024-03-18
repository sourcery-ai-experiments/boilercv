<#.SYNOPSIS
Sync Python dependencies.#>
Param(
    # Python version.
    [string]$Version,
    # Sync to highest dependencies.
    [switch]$High,
    # Recompile dependencies.
    [switch]$Compile,
    # Add all local dependency compilations to the lock.
    [switch]$Lock,
    # Don't update submodules.
    [switch]$NoUpdateSubmodules,
    # Don't sync local dev configs.
    [switch]$NoSyncLocalDevConfigs,
    # Don't install pre-commit hooks.
    [switch]$NoInstallHooks,
    # Don't recopy the template.
    [switch]$NoCopy,
    # Don't sync other items.
    [switch]$NoOtherSync

)

# ? Fail early
. 'scripts/Set-StrictErrors.ps1'
# ? Allow disabling CI when in CI, in order to test local dev workflows
$Env:CI = $Env:SYNC_PY_DISABLE_CI ? $null : $Env:CI

function Sync-Py {
    <#.SYNOPSIS
    Sync Python dependencies.#>

    '***SYNCING' | Write-PyProgress
    $py = Get-Py $Version
    # ? Install directly to system if in CI, breaking system packages if needed
    $System = $Env:CI ? '--system --break-system-packages' : ''
    # ? Python scripts for utilities not invoked with e.g. `python -m` (e.g. pre-commit)
    $scripts = $(Split-Path $py)

    'INSTALLING UV' | Write-PyProgress
    Invoke-Expression "$py -m pip install $(Get-Content 'requirements/uv.in')"

    'INSTALLING TOOLS' | Write-PyProgress
    # ? Install the `boilercv_tools` Python module
    Invoke-Expression "$py -m uv pip install $System --editable scripts/."

    if (!$Env:CI) {
        if (!$NoUpdateSubmodules) {
            'SYNCING SUBMODULES' | Write-PyProgress
            git submodule update --init --merge
            'SUBMODULES SYNCED' | Write-PyProgress -Done
        }
        if (!$NoSyncLocalDevConfigs) {
            'SYNCING LOCAL DEV CONFIGS' | Write-PyProgress
            Invoke-Expression "$py -m boilercv_tools sync-local-dev-configs"
            'LOCAL DEV CONFIGS SYNCED' | Write-PyProgress -Done
        }
        if (!$NoInstallHooks) {
            'INSTALLING MISSING PRE-COMMIT HOOKS' | Write-PyProgress
            Invoke-Expression "$scripts/pre-commit install"
        }
    }

    if ($Env:CI -and !$NoCopy) {
        'SYNCING PROJECT WITH TEMPLATE' | Write-PyProgress
        $head = git rev-parse HEAD:submodules/template
        Invoke-Expression "$py -m copier update --defaults --vcs-ref $head"
    }

    'SYNCING DEPENDENCIES' | Write-PyProgress
    $High = $High ? '--high' : ''
    # ? Compile or retrieve compiled dependencies
    if ($Compile) { $comp = Invoke-Expression "$py -m boilercv_tools compile $High" }
    else { $comp = Invoke-Expression "$py -m boilercv_tools get-comp $High" }
    # ? Lock
    if ($Lock) { Invoke-Expression "$py -m boilercv_tools lock" }
    # ? Sync
    if (!$Env:CI -and (Test-FileLock "$scripts/dvc$($IsWindows ? '.exe': '')")) {
        'The DVC VSCode extension is locking `dvc.exe`. INSTALLING INSTEAD OF SYNCING' |
            Write-PyProgress
        $compNoDvc = $comp | Get-Item | Get-Content | Select-String -Pattern '^(?!dvc[^-])'
        $compNoDvc | Set-Content $comp
        Invoke-Expression "$py -m uv pip install $System --requirement $comp"
        'INSTALL COMPLETE (Disable the VSCode DVC extension or close VSCode and sync in an external terminal to perform a full sync)' |
            Write-PyProgress -Done
    }
    else {
        Invoke-Expression "$py -m uv pip sync $System $comp"
        'SYNCED' | Write-PyProgress -Done
    }

    if (!$Env:CI -and !$NoOtherSync) {
        'SYNCING BOILERCV PARAMS' | Write-PyProgress
        Invoke-Expression "$PY -m boilercv.models.params"
        'SYNCED BOILERCV PARAMS' | Write-PyProgress -Done
        'HIDING DOCS NOTEBOOK INPUTS' | Write-PyProgress
        Invoke-Expression "$PY -m boilercv.docs"
        'DOCS NOTEBOOK INPUTS HIDDEN' | Write-PyProgress -Done
    }

    Write-Host ''
    '...DONE ***' | Write-PyProgress -Done
}


function Get-Py {
    <#.SYNOPSIS
    Get Python interpreter, global in CI, or activated virtual environment locally.#>
    Param([Parameter(ValueFromPipeline)][string]$Version)
    begin { $venvPath = '.venv' }
    process {
        $Version = $Version ? $Version : (Get-PyDevVersion)
        $GlobalPy = Get-PyGlobal $Version
        if ($Env:CI) {
            "SYNCING GLOBAL PYTHON: $GlobalPy" | Write-PyProgress
            return $GlobalPy
        }
        if (!(Test-Path $venvPath)) {
            "CREATING VIRTUAL ENVIRONMENT: $venvPath" | Write-PyProgress
            Invoke-Expression "$GlobalPy -m venv $venvPath"
        }
        $VenvPy = Start-PyEnv $venvPath
        $foundVersion = Invoke-Expression "$VenvPy --version"
        if ($foundVersion |
                Select-String -Pattern "^Python $([Regex]::Escape($Version))\.\d+$") {
            "SYNCING VIRTUAL ENVIRONMENT: $(Resolve-Path $VenvPy -Relative)" |
                Write-PyProgress
            return $VenvPy
        }
        "REMOVING VIRTUAL ENVIRONMENT WITH INCORRECT PYTHON: $Env:VIRTUAL_ENV" |
            Write-PyProgress -Done
        Remove-Item -Recurse -Force $Env:VIRTUAL_ENV
        return Get-Py $Version
    }
}

function Get-PyDevVersion {
    <#.SYNOPSIS
    Get the expected version of Python for development, from '.copier-answers.yml'.#>
    $ver_pattern = '^python_version:\s?["'']([^"'']+)["'']$'
    $re = Get-Content '.copier-answers.yml' | Select-String -Pattern $ver_pattern
    return $re.Matches.Groups[1].value
}

function Get-PyGlobal {
    <#.SYNOPSIS
    Get global Python interpreter.#>
    Param([Parameter(Mandatory, ValueFromPipeline)][string]$Version)
    process {
        if ((Test-Command 'py') -and
        (py '--list' | Select-String -Pattern "^\s?-V:$([Regex]::Escape($Version))")) {
            return "py -$Version"
        }
        elseif (Test-Command "python$Version") { return "python$Version" }
        elseif (Test-Command 'python') { return 'python' }
        throw "Expected Python $Version, which does not appear to be installed. Ensure it is installed (e.g. from https://www.python.org/downloads/) and run this script again."
    }
}

function Start-PyEnv {
    <#.SYNOPSIS
    Activate and get the Python interpreter for the virtual environment.#>
    Param([Parameter(Mandatory, ValueFromPipeline)][string]$venvPath)
    process {
        if ($IsWindows) { $bin = 'Scripts'; $py = 'python.exe' }
        else { $bin = 'bin'; $py = 'python' }
        Invoke-Expression "$venvPath/$bin/Activate.ps1"
        return "$Env:VIRTUAL_ENV/$bin/$py"
    }
}


function Write-PyProgress {
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

function Test-Command {
    <#.SYNOPSIS
    Like `Get-Command` but errors are ignored.#>
    return Get-Command @args -ErrorAction 'Ignore'
}

function Test-FileLock {
    <#.SYNOPSIS
    Test whether a file handle is locked.#>
    Param ([parameter(Mandatory, ValueFromPipeline)][string]$Path)
    process {
        if ( !(Test-Path $Path) ) { return $false }
        try {
            if ($handle = (
                    New-Object 'System.IO.FileInfo' $Path).Open([System.IO.FileMode]::Open,
                    [System.IO.FileAccess]::ReadWrite,
                    [System.IO.FileShare]::None)
            ) { $handle.Close() }
            return $false
        }
        catch [System.IO.IOException], [System.UnauthorizedAccessException] { return $true }
    }
}

Sync-Py
