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

Import-Module ./scripts/Common.psm1, ./scripts/CrossPy.psm1

# ? Stop on first error and enable native command error propagation.
$ErrorActionPreference = 'Stop'
$PSNativeCommandUseErrorActionPreference = $true
$PSNativeCommandUseErrorActionPreference | Out-Null

# ? Allow toggling CI in order to test local dev workflows
$Env:CI = $Env:SYNC_PY_DISABLE_CI ? $null : $Env:CI

# ? Get Python interpreter, prepare to sync
'*** SYNCING' | Write-Progress
$re = Get-Content .copier-answers.yml |
    Select-String -Pattern '^python_version:\s?["'']([^"'']+)["'']$'
$pyDevVersion = $re.Matches.Groups[1].value
$Version = $Version ? $Version : $pyDevVersion
if ($Env:CI) {
    $py = $Version | Get-PySystem
    "Using $(Resolve-Path $py)" | Write-Progress -Info
}
else {
    $py = $Version | Get-Py
    "Using $(Resolve-Path $py -Relative)" | Write-Progress -Info
}

# ? Don't pre-sync or post-sync in CI
$NoPreSync = $NoPreSync ? $NoPreSync : [bool]$Env:CI
$NoPostSync = $NoPostSync ? $NoPostSync : [bool]$Env:CI
(
    $($Env:CI ? 'Will act as if in CI' : 'Will act as if running locally'),
    $($NoPreSync ? "Won't run pre-sync tasks" : 'Will run pre-sync tasks'),
    $($NoPostSync ? "Won't run post-sync tasks" : 'Will run post-sync tasks')
) | Write-Progress -Info

# ? Install dependencies for pre-sync tasks and syncing
'INSTALLING PRE-SYNC DEPENDENCIES' | Write-Progress
pip install --quiet --requirement=requirements/sync.in
'PRE-SYNC DEPENDENCIES INSTALLED' | Write-Progress -Done

'INSTALLING TOOLS' | Write-Progress
# ? Install the `boilercv_tools` Python module
if ($Env:CI) { uv pip install --system --break-system-packages --editable=scripts }
else { uv pip install --editable=scripts }

# ? Pre-sync
if (!$NoPreSync) {
    '*** RUNNING PRE-SYNC TASKS' | Write-Progress
    'SYNCING SUBMODULES' | Write-Progress
    git submodule update --init --merge
    'SUBMODULES SYNCED' | Write-Progress -Done
    '' | Write-Host
    '*** PRE-SYNC DONE ***' | Write-Progress -Done
}
if ($Env:CI) {
    'SYNCING PROJECT WITH TEMPLATE' | Write-Progress
    $head = git rev-parse HEAD:submodules/template
    copier update --defaults --vcs-ref=$head
    'PROJECT SYNCED WITH TEMPLATE' | Write-Progress
}

# ? Compile or retrieve compiled dependencies
if ($Compile) {
    'COMPILING' | Write-Progress
    $comp = boilercv_tools compile --high=$High
    'COMPILED' | Write-Progress -Done
}
else {
    'GETTING COMPILATION FROM LOCK, COMPILING IF MISSING' | Write-Progress
    $comp = boilercv_tools get-comp --high=$High
    'COMPILATION FOUND OR COMPILED' | Write-Progress -Done
}

# ? Lock
if ($Lock) {
    'LOCKING' | Write-Progress
    boilercv_tools lock
    'LOCKED' | Write-Progress -Done
}

# ? Sync
if ($Env:CI -and ('dvc' | Test-CommandLock)) {
    'The DVC VSCode extension is locking `dvc.exe` (Disable the VSCode DVC extension or close VSCode and sync in an external terminal to perform a full sync)' |
        Write-Progress -Info
    'INSTALLING INSTEAD OF SYNCING' |
        Write-Progress
    $compNoDvc = Get-Content $comp | Select-String -Pattern '^(?!dvc[^-])'
    $compNoDvc | Set-Content $comp
    if ($Env:CI) { uv pip install --system --break-system-packages --editable=$comp }
    else { uv pip install --requirement=$comp }
    'DEPENDENCIES INSTALLED' | Write-Progress -Done
}
else {
    'SYNCING DEPENDENCIES' | Write-Progress
    if ($Env:CI) { uv pip sync --system --break-system-packages $comp }
    else { uv pip sync $comp }
    'DEPENDENCIES SYNCED' | Write-Progress -Done
}

# ? Post-sync
if (!$NoPostSync) {
    '*** RUNNING POST-SYNC TASKS' | Write-Progress
    'SYNCING LOCAL DEV CONFIGS' | Write-Progress
    boilercv_tools 'sync-local-dev-configs'
    'LOCAL DEV CONFIGS SYNCED' | Write-Progress -Done
    'INSTALLING PRE-COMMIT HOOKS' | Write-Progress
    pre-commit install
    'SYNCING BOILERCV PARAMS' | Write-Progress
    & $py -m boilercv.models.params
    'BOILERCV PARAMS SYNCED' | Write-Progress
    '' | Write-Host
    '*** POST-SYNC TASKS COMPLETE ***' | Write-Progress -Done
}

'' | Write-Host
'*** DONE ***' | Write-Progress -Done
