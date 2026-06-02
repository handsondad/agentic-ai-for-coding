param(
    [string]$GitHubToken = "",
    [string]$Repository = "",
    [string]$AgentCommand = "",
    [switch]$NoSessionUpdate,
    [switch]$Force
)

$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = (Resolve-Path (Join-Path $scriptDir "..\..\..")).Path

function Resolve-RepositoryFromGit {
    param([string]$Root)

    $gitPath = Get-Command git -ErrorAction SilentlyContinue
    if (-not $gitPath) {
        return ""
    }

    $remote = (& git -C $Root remote get-url origin 2>$null)
    if (-not $remote) {
        return ""
    }

    $match = [regex]::Match($remote.Trim(), "github\.com[:/](?<owner>[^/]+)/(?<repo>[^/.]+)(?:\.git)?$")
    if (-not $match.Success) {
        return ""
    }

    return "{0}/{1}" -f $match.Groups["owner"].Value, $match.Groups["repo"].Value
}

function Read-SecretValue {
    param([string]$Prompt)

    $secure = Read-Host $Prompt -AsSecureString
    $bstr = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($secure)
    try {
        return [Runtime.InteropServices.Marshal]::PtrToStringBSTR($bstr)
    }
    finally {
        [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($bstr)
    }
}

function Set-EnvValue {
    param(
        [string]$Name,
        [string]$Value,
        [switch]$IsSecret
    )

    $existing = [Environment]::GetEnvironmentVariable($Name, "User")
    if ($existing -and -not $Force) {
        Write-Host "Skip ${Name}: already exists in User scope (use -Force to overwrite)." -ForegroundColor Yellow
        if (-not $NoSessionUpdate) {
            Set-Item -Path "Env:$Name" -Value $existing
        }
        return
    }

    [Environment]::SetEnvironmentVariable($Name, $Value, "User")
    if (-not $NoSessionUpdate) {
        Set-Item -Path "Env:$Name" -Value $Value
    }

    if ($IsSecret) {
        Write-Host "Set $Name in User scope." -ForegroundColor Green
    }
    else {
        Write-Host "Set $Name=$Value in User scope." -ForegroundColor Green
    }
}

Set-Location $repoRoot

if (-not $Repository) {
    if ($env:GITHUB_REPOSITORY) {
        $Repository = $env:GITHUB_REPOSITORY
    }
    else {
        $Repository = Resolve-RepositoryFromGit -Root $repoRoot
    }
}

if (-not $Repository) {
    $Repository = Read-Host "Enter GITHUB_REPOSITORY (owner/repo)"
}

if (-not $Repository -or $Repository -notmatch "^[^/]+/[^/]+$") {
    throw "Invalid repository format. Expected owner/repo."
}

if (-not $GitHubToken) {
    if ($env:GITHUB_TOKEN) {
        $GitHubToken = $env:GITHUB_TOKEN
    }
    else {
        $GitHubToken = Read-SecretValue -Prompt "Enter GITHUB_TOKEN"
    }
}

if (-not $GitHubToken) {
    throw "GITHUB_TOKEN cannot be empty."
}

if (-not $AgentCommand) {
    if ($env:AUTOMATION_AGENT_COMMAND) {
        $AgentCommand = $env:AUTOMATION_AGENT_COMMAND
    }
    else {
        $AgentCommand = 'powershell -NoProfile -ExecutionPolicy Bypass -File ".github/automation/scripts/run-agent-adapter.ps1" -Workspace "{workspace}" -PromptFile "{prompt}" -IssueNumber "{issue_number}" -IssueTitle "{issue_title}" -IssueUrl "{issue_url}" -Workflow "{workflow}"'
    }
}

$backendCommand = [Environment]::GetEnvironmentVariable("AUTOMATION_ADAPTER_BACKEND_COMMAND", "User")
if (-not $backendCommand) {
    if ($env:AUTOMATION_ADAPTER_BACKEND_COMMAND) {
        $backendCommand = $env:AUTOMATION_ADAPTER_BACKEND_COMMAND
    }
    else {
        $backendCommand = 'your-agent-cli --workspace "{workspace}" --prompt-file "{prompt}"'
    }
}

Set-EnvValue -Name "GITHUB_TOKEN" -Value $GitHubToken -IsSecret
Set-EnvValue -Name "GITHUB_REPOSITORY" -Value $Repository
Set-EnvValue -Name "AUTOMATION_AGENT_COMMAND" -Value $AgentCommand
Set-EnvValue -Name "AUTOMATION_ADAPTER_BACKEND_COMMAND" -Value $backendCommand

Write-Host ""
Write-Host "Automation environment is ready." -ForegroundColor Cyan
Write-Host "- GITHUB_REPOSITORY: $Repository"
Write-Host "- AUTOMATION_AGENT_COMMAND: $AgentCommand"
Write-Host "- AUTOMATION_ADAPTER_BACKEND_COMMAND: $backendCommand"
Write-Host "- GITHUB_TOKEN: [hidden]"
Write-Host ""
Write-Host "Next step: powershell -NoProfile -ExecutionPolicy Bypass -File .github/automation/scripts/run-once.ps1" -ForegroundColor Cyan
