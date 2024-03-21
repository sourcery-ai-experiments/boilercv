<#.SYNOPSIS
Stop on first error and enable native command error propagation.#>
$ErrorActionPreference = 'Stop'
$PSNativeCommandUseErrorActionPreference = $true
$PSNativeCommandUseErrorActionPreference | Out-Null
