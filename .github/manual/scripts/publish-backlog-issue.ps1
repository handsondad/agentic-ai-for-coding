param(
    [Parameter(Mandatory = $true)]
    [string]$File,
    [string]$Repo = "",
    [switch]$AllowDraft,
    [switch]$DryRun,
    [string]$PythonExe = "python"
)

$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$runner = Join-Path $scriptDir "publish-backlog-issue.py"

$args = @($runner, $File)
if ($Repo) { $args += @("--repo", $Repo) }
if ($AllowDraft) { $args += "--allow-draft" }
if ($DryRun) { $args += "--dry-run" }

& $PythonExe $args
if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
}
