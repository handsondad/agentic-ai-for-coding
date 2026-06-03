param(
    [int]$IssueNumber = 0,
    [string]$IssueFile = "",
    [string]$Workflow = "WORKFLOW.md",
    [string]$PythonExe = "python"
)

$ErrorActionPreference = "Stop"

function Use-UserEnvFallback {
    param([string]$Name)

    $currentValue = (Get-Item -Path ("Env:{0}" -f $Name) -ErrorAction SilentlyContinue).Value
    if ($currentValue) {
        return
    }

    $userValue = [Environment]::GetEnvironmentVariable($Name, "User")
    if ($userValue) {
        Set-Item -Path ("Env:{0}" -f $Name) -Value $userValue
    }
}

if (($IssueNumber -gt 0) -and $IssueFile) {
    throw "Specify only one of -IssueNumber or -IssueFile."
}

if (($IssueNumber -le 0) -and (-not $IssueFile)) {
    throw "Specify either -IssueNumber or -IssueFile."
}

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$runner = Join-Path $scriptDir "prepare-single-issue.py"

Use-UserEnvFallback -Name "GITHUB_TOKEN"
Use-UserEnvFallback -Name "GITHUB_REPOSITORY"

if ($IssueNumber -gt 0) {
    & $PythonExe $runner "--workflow" $Workflow "--issue-number" $IssueNumber
}
else {
    & $PythonExe $runner "--workflow" $Workflow "--issue-file" $IssueFile
}
if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
}