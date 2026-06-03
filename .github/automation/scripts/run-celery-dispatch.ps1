param(
    [string]$Workflow = "WORKFLOW.md",
    [string]$Broker = "",
    [string]$Backend = "",
    [string]$Queue = "",
    [string]$LogLevel = "INFO",
    [switch]$Once,
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

if (-not $env:GITHUB_TOKEN) {
    throw "Environment variable GITHUB_TOKEN is required."
}

if (-not $env:GITHUB_REPOSITORY) {
    throw "Environment variable GITHUB_REPOSITORY is required, e.g. owner/repo."
}

Set-Location $repoRoot

if ($Broker) {
    $env:AUTOMATION_CELERY_BROKER_URL = $Broker
}
if ($Backend) {
    $env:AUTOMATION_CELERY_RESULT_BACKEND = $Backend
}
if ($Queue) {
    $env:AUTOMATION_CELERY_QUEUE = $Queue
}

$args = @(
    ".github/automation/cli.py",
    "--workflow", $Workflow,
    "--log-level", $LogLevel
)

if ($Once) {
    $args += "--once"
}

& $PythonExe @args
if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
}
