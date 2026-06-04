param(
    [ValidateSet("quick", "full")]
    [string]$Mode = "full",
    [string]$RepoRoot = "",
    [string]$PythonExe = "python"
)

$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$runner = Join-Path $scriptDir "run-quality-gate.py"

if ($RepoRoot) {
    & $PythonExe $runner "--mode" $Mode "--repo-root" $RepoRoot
}
else {
    & $PythonExe $runner "--mode" $Mode
}

if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
}
