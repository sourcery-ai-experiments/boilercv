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
    # Don't run pre-sync actions.
    [switch]$NoPreSync,
    # Don't run post-sync actions.
    [switch]$NoPostSync
)

# ? Fail early
. 'scripts/Set-StrictErrors.ps1'
# ? Allow disabling CI when in CI, in order to test local dev workflows
$Env:CI = $Env:SYNC_PY_DISABLE_CI ? $null : $Env:CI
# ? Don't pre-sync or post-sync in CI
$NoPreSync = $NoPreSync ? $NoPreSync : [bool]$Env:CI
$NoPostSync = $NoPostSync ? $NoPostSync : [bool]$Env:CI
# ? Core dependencies needed for syncing
$PRE_SYNC_DEPENDENCIES = 'requirements/sync.in'

function Sync-Py {
    <#.SYNOPSIS
    Sync Python dependencies.#>

    # ? Print invocation details
    '***SYNCING' | Write-PyProgress
    $Version = $Version ? $Version : (Get-PyDevVersion)
    if ($Env:CI) {
        $py = Get-PySystem $Version
        "USING $(Resolve-Path $py)" | Write-PyProgress -Info
    }
    else {
        $py = Get-Py $Version
        "USING $(Resolve-Path $py -Relative)" | Write-PyProgress -Info
    }
    $($Env:CI ? 'Will act as if in CI' : 'Will act as if running locally') | Write-PyProgress -Info
    $($NoPreSync ? "Won't run pre-sync tasks" : 'Will run pre-sync tasks') | Write-PyProgress -Info
    $($NoPostSync ? "Won't run post-sync tasks" : 'Will run post-sync tasks') | Write-PyProgress -Info
    # ? Python environment modules and scripts
    $pyModules = "$py -m"
    $pyScripts = Get-PyScripts $py
    $pip = "$pyScripts/pip"
    $uv = "$pyScripts/uv"
    $tools = "$pyScripts/boilercv_tools"
    $dvc = "$pyScripts/dvc"
    $uvPip = "$uv pip"

    # ? Install directly to system if in CI, breaking system packages if needed
    $System = $Env:CI ? '--system --break-system-packages' : ''
    $install = "$uvPip install $System"
    $sync = "$uvPip sync $System"

    'INSTALLING DEPENDENCIES FOR SYNCING' | Write-PyProgress
    Invoke-Expression "$pip install --requirement $PRE_SYNC_DEPENDENCIES"

    'INSTALLING TOOLS' | Write-PyProgress
    # ? Install the `boilercv_tools` Python module
    Invoke-Expression "$install --no-cache --editable scripts/."

    if (!$NoPreSync) {
        'RUNNING PRE-SYNC TASKS' | Write-PyProgress
        'SYNCING SUBMODULES' | Write-PyProgress
        git submodule update --init --merge
        'PRE-SYNC DONE' | Write-PyProgress -Done
    }
    if ($Env:CI) {
        'SYNCING PROJECT WITH TEMPLATE' | Write-PyProgress
        $head = git rev-parse HEAD:submodules/template
        Invoke-Expression "$pyScripts/copier update --defaults --vcs-ref $head"
        'PROJECT SYNCED WITH TEMPLATE' | Write-PyProgress
    }

    'SYNCING DEPENDENCIES' | Write-PyProgress
    $High = $High ? '--high' : ''

    # ? Compile or retrieve compiled dependencies
    if ($Compile) { $comp = Invoke-Expression "$tools compile $High" }
    else { $comp = Invoke-Expression "$tools get-comp $High" }

    # ? Lock
    if ($Lock) { Invoke-Expression "$tools lock" }

    # ? Sync
    if ($Env:CI -and (Test-CommandLock $dvc)) {
        'The DVC VSCode extension is locking `dvc.exe`. INSTALLING INSTEAD OF SYNCING' |
            Write-PyProgress
        $compNoDvc = $comp | Get-Item | Get-Content | Select-String -Pattern '^(?!dvc[^-])'
        $compNoDvc | Set-Content $comp
        Invoke-Expression "$install --requirement $comp"
        'DEPENDENCIES INSTALLED (Disable the VSCode DVC extension or close VSCode and sync in an external terminal to perform a full sync)' |
            Write-PyProgress -Done
    }
    else {
        Invoke-Expression "$sync $comp"
        'DEPENDENCIES SYNCED' | Write-PyProgress -Done
    }

    if (!$NoPostSync) {
        'RUNNING POST-SYNC TASKS' | Write-PyProgress
        'SYNCING LOCAL DEV CONFIGS' | Write-PyProgress
        Invoke-Expression "$tools sync-local-dev-configs"
        'LOCAL DEV CONFIGS SYNCED' | Write-PyProgress -Done
        'INSTALLING PRE-COMMIT HOOKS' | Write-PyProgress
        Invoke-Expression "$pyScripts/pre-commit install"
        'SYNCING BOILERCV PARAMS' | Write-PyProgress
        Invoke-Expression "$pyModules boilercv.models.params"
        'GITHUB ACTIONS WORKFLOWS IN USE IN THIS REPO:' | Write-PyProgress
        Invoke-Expression "$tools get-actions"
        'POST-SYNC TASKS COMPLETE' | Write-PyProgress -Done
    }

    Write-Host ''
    '...DONE ***' | Write-PyProgress -Done
}

# * -------------------------------------------------------------------------------- * #
# * CUSTOM FUNCTIONS

function Get-PyDevVersion {
    <#.SYNOPSIS
    Get the expected version of Python for development, from '.copier-answers.yml'.#>
    $ver_pattern = '^python_version:\s?["'']([^"'']+)["'']$'
    $re = Get-Content '.copier-answers.yml' | Select-String -Pattern $ver_pattern
    return $re.Matches.Groups[1].value
}

function Test-CommandLock {
    <#.SYNOPSIS
    Test whether a handle to a command is locked.#>
    Param ([parameter(Mandatory, ValueFromPipeline)][string]$Path)
    process {
        if (!(Test-Command $Path)) { return $false }
        return Get-Command $Path | Test-FileLock
    }
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

# * -------------------------------------------------------------------------------- * #
# * BASIC FUNCTIONS

function Get-Py {
    <#.SYNOPSIS
    Get virtual environment Python interpreter, creating it if necessary.#>
    Param([Parameter(Mandatory, ValueFromPipeline)][string]$Version)
    begin { $venvPath = '.venv' }
    process {
        $SysPy = Get-PySystem $Version
        if (!(Test-Path $venvPath)) {
            "CREATING VIRTUAL ENVIRONMENT: $venvPath" | Write-PyProgress
            Invoke-Expression "$SysPy -m venv $venvPath"
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

function Get-PySystem {
    <#.SYNOPSIS
    Get system Python interpreter.#>
    Param([Parameter(Mandatory, ValueFromPipeline)][string]$Version)
    process {
        if ((Test-Command 'py') -and (py '--list' | Select-String -Pattern "^\s?-V:$([Regex]::Escape($Version))")) {
            $py = "py -$Version"
        }
        elseif (Test-Command ($py = "python$Version")) { }
        elseif (Test-Command ($py = 'python')) { }
        else { throw "Expected Python $Version, which does not appear to be installed. Ensure it is installed (e.g. from https://www.python.org/downloads/) and run this script again." }
        return Invoke-Expression "$py -c 'from sys import executable; print(executable)'"
    }
}

function Get-PyScripts {
    <#.SYNOPSIS
    Get the Python scripts directory.#>
    Param([Parameter(Mandatory, ValueFromPipeline)][string]$Path)
    process {
        $pythonRoot = $(Split-Path $Path)
        $bin = $IsWindows ? 'Scripts' : 'bin'
        if (($pythonRoot | Get-Item | Select-Object -ExpandProperty Name) -eq $bin) {
            return $pythonRoot
        }
        return "$pythonRoot/$bin"
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

function Test-Command {
    <#.SYNOPSIS
    Like `Get-Command` but errors are ignored.#>
    return Get-Command @args -ErrorAction 'Ignore'
}

function Write-PyProgress {
    <#.SYNOPSIS
    Write progress and completion messages.#>
    Param(
        [Parameter(Mandatory, ValueFromPipeline)][string]$Message,
        [switch]$Done,
        [switch]$Info
    )
    begin {
        $InProgress = !$Done -and !$Info
        if ($Info) { $Color = 'Magenta' }
        elseif ($Done) { $Color = 'Green' }
        else { $Color = 'Yellow' }
    }
    process {
        if ($InProgress) { Write-Host }
        Write-Host "$Message$($InProgress ? '...' : '')" -ForegroundColor $Color
    }
}

Sync-Py
