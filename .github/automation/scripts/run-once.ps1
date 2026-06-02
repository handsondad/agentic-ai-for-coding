param(
    [string]$Workflow = "WORKFLOW.md",
    [string]$LogLevel = "INFO",
    [string]$PythonExe = "python"
)

$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = (Resolve-Path (Join-Path $scriptDir "..\..\..")).Path

if (-not $env:GITHUB_TOKEN) {
    throw "Environment variable GITHUB_TOKEN is required."
}

if (-not $env:GITHUB_REPOSITORY) {
    throw "Environment variable GITHUB_REPOSITORY is required, e.g. owner/repo."
}

Set-Location $repoRoot

& $PythonExe ".github/automation/cli.py" --once --workflow $Workflow --log-level $LogLevel
if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
}
