param(
    [Parameter(Mandatory = $true)]
    [string]$Workspace,

    [Parameter(Mandatory = $true)]
    [string]$PromptFile,

    [string]$IssueNumber = "",
    [string]$IssueTitle = "",
    [string]$IssueUrl = "",
    [string]$Workflow = "",
    [string]$BackendCommand = ""
)

$ErrorActionPreference = "Stop"

function Render-Template {
    param(
        [string]$Template,
        [hashtable]$Values
    )

    $rendered = $Template
    foreach ($key in $Values.Keys) {
        $token = "{$key}"
        $rendered = $rendered.Replace($token, [string]$Values[$key])
    }
    return $rendered
}

if (-not (Test-Path -LiteralPath $Workspace)) {
    throw "Workspace not found: $Workspace"
}

if (-not (Test-Path -LiteralPath $PromptFile)) {
    throw "Prompt file not found: $PromptFile"
}

if (-not $BackendCommand) {
    $BackendCommand = $env:AUTOMATION_ADAPTER_BACKEND_COMMAND
}

if (-not $BackendCommand) {
    throw @"
Missing AUTOMATION_ADAPTER_BACKEND_COMMAND.

Set it to your real agent command template, for example:
  your-agent-cli --workspace "{workspace}" --prompt-file "{prompt}"

Available placeholders:
  {workspace} {prompt} {issue_number} {issue_title} {issue_url} {workflow}
"@
}

$context = @{
    workspace    = $Workspace
    prompt       = $PromptFile
    issue_number = $IssueNumber
    issue_title  = $IssueTitle
    issue_url    = $IssueUrl
    workflow     = $Workflow
}

$rendered = Render-Template -Template $BackendCommand -Values $context

Write-Host "[adapter] workspace=$Workspace"
Write-Host "[adapter] prompt=$PromptFile"
Write-Host "[adapter] command=$rendered"

Push-Location -LiteralPath $Workspace
try {
    $cmdExe = if ($env:ComSpec) { $env:ComSpec } else { "cmd.exe" }
    & $cmdExe /d /s /c $rendered
    exit $LASTEXITCODE
}
finally {
    Pop-Location
}
