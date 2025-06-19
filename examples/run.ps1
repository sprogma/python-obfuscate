<#
    .SYNOPSIS
        This script should be used to run "one" compiler from powershell/pwsh

    .DESCRIPTION
        "one" compiler generate one python expression from provided code.
        At the moment, it supports not all python keywords, and sometimes
        not show errors (place there them are)

        To see supported constructions see "support.md"
        (on github: https://github.com/sprogma/python-obfuscate/blob/main/suppot.md)

    .EXAMPLE

        ./run.ps1 -Files a.py b.py -Destination res.py -RunAfter'

        compile a.py and b.py (one of them can import another) into res.py, and run resulting program.

    .EXAMPLE

        Get-ChildItem -Recurse *.py -Exclude tests.py | ./run.ps1 -Destination $null -PassThru | Measure-Object -line

        compile all files excluding test.py using pipe, not save to file, see how many lines it consume, must be one :)
#>
[CmdletBinding(HelpUri = "https://github.com/sprogma/python-obfuscate")]
param(
    # Array of files to compile. If there are many files, compiler can found circular import dependence and fail.
    [Parameter(ValueFromPipeline = $true, Mandatory = $true)]
    [string[]]$Files,
    # Path to save file (default is "out.py"), if null, not save result
    [AllowEmptyString()]
    [string]$Destination = "out.py",
    # If is on, script send resulting code both into stdout and $Destination file.
    [switch]$PassThru,
    # If is on, run resulting file
    [switch]$RunAfter,
    # Provide python executable (default is "py.exe" for Windows and "python3" for other OS.)
    [AllowEmptyString()]
    [string]$PythonExecutablePreference=$null
)

# guess python executable by platform
$PythonExecutable = ($IsWindows ? "py.exe" : "python3")

if ($PythonExecutablePreference)
{
    $PythonExecutable = $PythonExecutablePreference
}

if ($input)
{
    $Files = $input
}

if ($Destination)
{
    & $PythonExecutable one.py @Files -o $Destination
    $result = Get-Content $Destination -Raw
}
else
{
    $result = & $PythonExecutable one.py @Files -NoPrint
}


if ($PassThru)
{
    $result
}

if ($RunAfter)
{
    Write-Host "Run result:" -ForegroundColor Green
    & $PythonExecutable $Destination
}