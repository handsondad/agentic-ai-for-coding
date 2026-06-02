param(
    [string]$Workflow = "WORKFLOW.md",
    [string]$LogLevel = "INFO",
    [string]$PythonExe = "python"
)

$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = (Resolve-Path (Join-Path $scriptDir "..\..\..")).Path

function Use-UserEnvFallback {
    param([string]$Name)

    if (Test-Path -Path "Env:$Name") {
        return
    }

    $userValue = [Environment]::GetEnvironmentVariable($Name, "User")
    if ($userValue) {
        Set-Item -Path "Env:$Name" -Value $userValue
    }
}

Use-UserEnvFallback -Name "GITHUB_TOKEN"
Use-UserEnvFallback -Name "GITHUB_REPOSITORY"
Use-UserEnvFallback -Name "AUTOMATION_CA_BUNDLE"
Use-UserEnvFallback -Name "AUTOMATION_TLS_NO_VERIFY"

if (-not $env:GITHUB_TOKEN) {
    throw "Environment variable GITHUB_TOKEN is required."
}

if (-not $env:GITHUB_REPOSITORY) {
    throw "Environment variable GITHUB_REPOSITORY is required, e.g. owner/repo."
}

Set-Location $repoRoot

& $PythonExe ".github/automation/cli.py" --workflow $Workflow --log-level $LogLevel
if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
}
