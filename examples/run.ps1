param(
    [string]$Path="examples/example.py",
    [string]$Destination = "examples/example_res.py",
    [switch]$PrintAfter,
    [switch]$RunAfter
)

$pythonExecutable = "py"


& $pythonExecutable one.py $Path -o $Destination

if ($PrintAfter)
{
    Write-Host "Resulting file:" -ForegroundColor Green
    Get-Content $Destination -Raw | Out-Host
}

if ($RunAfter)
{
    Write-Host "Run result:" -ForegroundColor Green
    & $pythonExecutable $Destination
}