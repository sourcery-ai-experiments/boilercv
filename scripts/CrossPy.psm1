<#.SYNOPSIS
Cross-platform support for getting system and virtual environment Python interpreters.#>

$command = 'from sys import executable; print(executable)'

function Get-Py {
    <#.SYNOPSIS
    Get virtual environment Python interpreter, creating it if necessary.#>
    Param([Parameter(Mandatory, ValueFromPipeline)][string]$Version)
    process {
        $SysPy = $Version | Get-PySystem
        if (!(Test-Path '.venv')) { bin/uv venv }
        $VenvPy = Start-PyVenv
        $foundVersion = & $VenvPy --version
        if ($foundVersion |
                Select-String -Pattern "^Python $([Regex]::Escape($Version))\.\d+$") {
            return $VenvPy
        }
        Remove-Item -Recurse -Force $Env:VIRTUAL_ENV
        return Get-Py $Version
    }
}

function Get-PySystem {
    <#.SYNOPSIS
    Get system Python interpreter.#>
    Param([Parameter(Mandatory, ValueFromPipeline)][string]$Version)
    begin { function Test-Command { return Get-Command @args -ErrorAction 'Ignore' } }
    process {
        if ((Test-Command 'py') -and (py '--list' | Select-String -Pattern [Regex]::Escape($Version))) {
            return & py -$Version -c $command
        }
        elseif (Test-Command ($py = "python$Version")) { }
        elseif (Test-Command ($py = 'python')) { }
        else { throw "Expected Python $Version, which does not appear to be installed. Ensure it is installed (e.g. from https://www.python.org/downloads/) and run this script again." }
        return & $py -c $command
    }
}

function Start-PyVenv {
    <#.SYNOPSIS
    Activate and get the Python interpreter for the virtual environment.#>
    if (Test-Path ('.venv/Scripts')) {
        Get-ChildItem '.venv/Scripts'
        .venv/Scripts/activate
        if (Test-Path '.venv/Scripts/python.exe') { return '.venv/Scripts/python.exe' }
        else { return '.venv/Scripts/python' }
    }
    Get-ChildItem '.venv/bin'
    .venv/bin/activate
    if (Test-Path '.venv/bin/python.exe') { return '.venv/bin/python.exe' }
    else { return '.venv/bin/python' }
}
