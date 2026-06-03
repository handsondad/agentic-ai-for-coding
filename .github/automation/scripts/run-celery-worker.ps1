param(
    [string]$Queue = "automation_issues",
    [string]$Broker = "redis://localhost:6379/0",
    [string]$Backend = "redis://localhost:6379/1",
    [int]$Concurrency = 2,
    [string]$LogLevel = "INFO",
    [string]$PythonExe = "python"
)

$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = (Resolve-Path (Join-Path $scriptDir "..\..\..")).Path

Set-Location $repoRoot

$env:PYTHONPATH = "$repoRoot/.github/automation"
$env:AUTOMATION_CELERY_BROKER_URL = $Broker
$env:AUTOMATION_CELERY_RESULT_BACKEND = $Backend
$env:AUTOMATION_CELERY_QUEUE = $Queue

& $PythonExe -m celery -A celery_tasks:celery_app worker --loglevel $LogLevel --concurrency $Concurrency --queues $Queue
if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
}
