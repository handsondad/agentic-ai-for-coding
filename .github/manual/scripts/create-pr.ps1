param(
    [Parameter(Mandatory = $true)]
    [string]$Title,
    [string]$BodyFile = "",
    [string]$Base = "",
    [string]$Head = "",
    [string]$IssueNumber = "",
    [switch]$Draft,
    [string]$PythonExe = "python"
)

$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$runner = Join-Path $scriptDir "create-pr.py"

$args = @($runner, "--title", $Title)
if ($BodyFile) { $args += @("--body-file", $BodyFile) }
if ($Base) { $args += @("--base", $Base) }
if ($Head) { $args += @("--head", $Head) }
if ($IssueNumber) { $args += @("--issue-number", $IssueNumber) }
if ($Draft) { $args += "--draft" }

& $PythonExe $args
if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
}
