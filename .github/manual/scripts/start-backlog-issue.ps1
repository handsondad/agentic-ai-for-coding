param(
    [Parameter(Mandatory = $true)]
    [ValidateSet("feature", "bug", "task")]
    [string]$Type,
    [Parameter(Mandatory = $true)]
    [string]$Title,
    [string]$Date = "",
    [string]$FolderDate = "",
    [string]$Slug = "",
    [string]$BaseBranch = "main",
    [string]$BranchPrefix = "backlog",
    [string]$OutputRoot = ".github/issues-backlog",
    [string]$Template = ".github/issues-backlog/TEMPLATE.md",
    [switch]$DryRun,
    [switch]$AllowDirty,
    [string]$PythonExe = "python"
)

$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$runner = Join-Path $scriptDir "start-backlog-issue.py"

$cmd = @(
    $runner,
    "--type", $Type,
    "--title", $Title,
    "--base-branch", $BaseBranch,
    "--branch-prefix", $BranchPrefix,
    "--output-root", $OutputRoot,
    "--template", $Template
)

if ($Date) {
    $cmd += @("--date", $Date)
}
if ($FolderDate) {
    $cmd += @("--folder-date", $FolderDate)
}
if ($Slug) {
    $cmd += @("--slug", $Slug)
}
if ($DryRun) {
    $cmd += "--dry-run"
}
if ($AllowDirty) {
    $cmd += "--allow-dirty"
}

& $PythonExe $cmd
if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
}
