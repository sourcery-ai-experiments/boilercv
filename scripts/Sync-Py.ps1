<#.SYNOPSIS
Sync Python dependencies.#>
Param(
    # Python version.
    [string]$Version,
    # Sync to highest dependencies.
    [switch]$High,
    # Add all local dependency compilations to the lock.
    [switch]$Lock,
    # Don't run pre-sync actions.
    [switch]$NoPreSync,
    # Don't run post-sync actions.
    [switch]$NoPostSync
)

Import-Module ./scripts/Common.psm1, ./scripts/CrossPy.psm1

'*** SYNCING' | Write-Progress

# ? Stop on first error and enable native command error propagation.
$ErrorActionPreference = 'Stop'
$PSNativeCommandUseErrorActionPreference = $true

# ? Allow toggling CI in order to test local dev workflows
$CI = $Env:SYNC_PY_DISABLE_CI ? $null : $Env:CI
$Env:UV_SYSTEM_PYTHON = $CI ? 'true' : 'false'

# ? Don't pre-sync or post-sync in CI
$NoPreSync = $NoPreSync ? $NoPreSync : [bool]$CI
$NoPostSync = $NoPostSync ? $NoPostSync : [bool]$CI
(
    $($CI ? 'Will act as if in CI' : 'Will act as if running locally'),
    $($NoPreSync ? "Won't run pre-sync tasks" : 'Will run pre-sync tasks'),
    $($NoPostSync ? "Won't run post-sync tasks" : 'Will run post-sync tasks')
) | Write-Progress -Info

# ? Install uv
$uvVersionRe = Get-Content 'requirements/uv.in' | Select-String -Pattern '^uv==(.+)$'
$uvVersion = $uvVersionRe.Matches.Groups[1].value
if ((Test-Path 'bin/uv*') -and (bin/uv --version | Select-String $uvVersion)) {
    'Correct uv already installed' | Write-Progress -Info
}
else {
    'INSTALLING UV' | Write-Progress
    $Env:CARGO_HOME = '.'
    if ($IsWindows) {
        $uvInstaller = "$([System.IO.Path]::GetTempPath())$([System.Guid]::NewGuid()).ps1"
        Invoke-RestMethod "https://github.com/astral-sh/uv/releases/download/$uvVersion/uv-installer.ps1" |
            Out-File $uvInstaller
        powershell -Command "$uvInstaller -NoModifyPath"
    }
    else {
        $Env:INSTALLER_NO_MODIFY_PATH = $true
        curl --proto '=https' --tlsv1.2 -LsSf "https://github.com/astral-sh/uv/releases/download/$uvVersion/uv-installer.sh" |
            sh
    }
    'UV INSTALLED' | Write-Progress -Done
}

# ? Synchronize local environment and return if not in CI
'INSTALLING TOOLS' | Write-Progress
$pyDevVersionRe = Get-Content '.copier-answers.yml' |
    Select-String -Pattern '^python_version:\s?["'']([^"'']+)["'']$'
$Version = $Version ? $Version : $pyDevVersionRe.Matches.Groups[1].value
if ($CI) {
    $py = $Version | Get-PySystem
    "Using $(Resolve-Path $py)" | Write-Progress -Info
}
else {
    $py = $Version | Get-Py
    "Using $(Resolve-Path $py -Relative)" | Write-Progress -Info
}
# ? Install the `boilercv_tools` Python module
bin/uv pip install --editable=scripts
'TOOLS INSTALLED' | Write-Progress -Done

# ? Pre-sync
if (!$NoPreSync) {
    '*** RUNNING PRE-SYNC TASKS' | Write-Progress
    'SYNCING SUBMODULES' | Write-Progress
    git submodule update --init --merge
    'SUBMODULES SYNCED' | Write-Progress -Done
    '' | Write-Host
    '*** PRE-SYNC DONE ***' | Write-Progress -Done
}

# ? Compile
'COMPILING' | Write-Progress
$Comps = & $py -m boilercv_tools compile
$Comp = $High ? $Comps[1] : $Comps[0]
'COMPILED' | Write-Progress -Done

# ? Sync
if ('dvc' | Test-CommandLock) {
    'The DVC VSCode extension is locking `dvc.exe` (Disable the VSCode DVC extension or close VSCode and sync in an external terminal to perform a full sync)' |
        Write-Progress -Info
    'INSTALLING INSTEAD OF SYNCING' |
        Write-Progress
    $CompNoDvc = Get-Content $Comp | Select-String -Pattern '^(?!dvc[^-])'
    $CompNoDvc | Set-Content $Comp
    bin/uv pip install --requirement=$Comp
    'DEPENDENCIES INSTALLED' | Write-Progress -Done
}
else {
    'SYNCING DEPENDENCIES' | Write-Progress
    bin/uv pip sync $Comp
    'DEPENDENCIES SYNCED' | Write-Progress -Done
}

# ? Post-sync
if (!$NoPostSync) {
    '*** RUNNING POST-SYNC TASKS' | Write-Progress
    'SYNCING LOCAL DEV CONFIGS' | Write-Progress
    & $py -m boilercv_tools 'sync-local-dev-configs'
    'LOCAL DEV CONFIGS SYNCED' | Write-Progress -Done
    'INSTALLING PRE-COMMIT HOOKS' | Write-Progress
    pre-commit install
    'SYNCING BOILERCV PARAMS' | Write-Progress
    & $py -m boilercv.models.params
    'BOILERCV PARAMS SYNCED' | Write-Progress
    '' | Write-Host
    '*** POST-SYNC DONE ***' | Write-Progress -Done
}
# ? Sync project with template in CI
if ($CI) {
    'SYNCING PROJECT WITH TEMPLATE' | Write-Progress
    scripts/Sync-Template.ps1 -Stay
    'PROJECT SYNCED WITH TEMPLATE' | Write-Progress
}

# ? Lock
if ($Lock) {
    'LOCKING' | Write-Progress
    & $py -m boilercv_tools lock
    'LOCKED' | Write-Progress -Done
}

'' | Write-Host
'*** DONE ***' | Write-Progress -Done

# ? Stop PSScriptAnalyzer from complaining about these "unused" variables
$PSNativeCommandUseErrorActionPreference, $NoModifyPath | Out-Null
