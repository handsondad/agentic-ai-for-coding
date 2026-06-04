"""Issue 执行流水线：worktree、AI 执行、质量检查、提交 PR。"""

from __future__ import annotations

import asyncio
import logging
import os
import shutil
import subprocess
from pathlib import Path

try:
    from .github_client import GitHubClient
    from .models import (
        GitHubIssue,
        PipelineResult,
        QualityGateResult,
        RuntimeSettings,
        slugify,
    )
except ImportError:
    from github_client import GitHubClient
    from models import (
        GitHubIssue,
        PipelineResult,
        QualityGateResult,
        RuntimeSettings,
        slugify,
    )

logger = logging.getLogger(__name__)


class PipelineError(RuntimeError):
    """流水线执行失败。"""


class IssuePipeline:
    """单个 Issue 的端到端执行器。"""

    def __init__(self, settings: RuntimeSettings, github: GitHubClient) -> None:
        self._settings = settings
        self._github = github

    async def run(self, issue: GitHubIssue) -> PipelineResult:
        """执行完整流水线并返回结果。"""
        branch_name = f"ai/issue-{issue.number}-{slugify(issue.title, 36)}"
        worktree_path = self._settings.workspace_root / f"issue-{issue.number}"

        self._settings.workspace_root.mkdir(parents=True, exist_ok=True)

        await self._prepare_worktree(worktree_path, branch_name)
        await self._render_issue_prompt(issue, worktree_path)

        if self._settings.hooks.before_run:
            await self._run_hook_command(
                hook_name="before_run",
                command=self._settings.hooks.before_run,
                cwd=worktree_path,
            )

        try:
            await self._run_agent(issue, worktree_path)
            quality_results = await self._run_quality_checks(
                issue, worktree_path, branch_name
            )
        finally:
            if self._settings.hooks.after_run:
                await self._run_hook_command(
                    hook_name="after_run",
                    command=self._settings.hooks.after_run,
                    cwd=worktree_path,
                )

        changed = await self._has_git_changes(worktree_path)
        if not changed:
            return PipelineResult(
                issue_number=issue.number,
                branch_name=branch_name,
                worktree_path=worktree_path,
                quality_results=quality_results,
                pr_url=None,
                changed=False,
            )

        await self._commit_and_push(issue, worktree_path, branch_name)

        pr_body = _build_pr_body(issue, quality_results)
        pr_title = f"fix: {issue.title} (closes #{issue.number})"
        pr_url = await self._github.create_pull_request(
            title=pr_title,
            body=pr_body,
            head_branch=branch_name,
            base_branch=self._settings.base_branch,
        )

        return PipelineResult(
            issue_number=issue.number,
            branch_name=branch_name,
            worktree_path=worktree_path,
            quality_results=quality_results,
            pr_url=pr_url,
            changed=True,
        )

    async def _prepare_worktree(self, path: Path, branch_name: str) -> None:
        skip_fetch = os.getenv("AUTOMATION_SKIP_GIT_FETCH", "").strip().lower() in {
            "1",
            "true",
            "yes",
        }
        if skip_fetch:
            logger.warning(
                "AUTOMATION_SKIP_GIT_FETCH enabled; skipping remote fetch step."
            )
        else:
            await self._run_command(
                f"git fetch origin {self._settings.base_branch}",
                cwd=self._settings.repo_root,
            )

        if not path.exists():
            await self._run_command(
                " ".join(
                    [
                        "git worktree add -B",
                        branch_name,
                        _quote(path),
                        f"origin/{self._settings.base_branch}",
                    ]
                ),
                cwd=self._settings.repo_root,
            )
            if self._settings.hooks.after_create:
                await self._run_hook_command(
                    hook_name="after_create",
                    command=self._settings.hooks.after_create,
                    cwd=path,
                )
            return

        status = await self._run_command(
            "git status --porcelain", cwd=path, check=False
        )
        if status.stdout.strip():
            raise PipelineError(f"工作目录存在未提交改动，请先清理: {path}")

        await self._run_command(
            f"git checkout -B {branch_name} origin/{self._settings.base_branch}",
            cwd=path,
        )

    async def _render_issue_prompt(
        self, issue: GitHubIssue, worktree_path: Path
    ) -> None:
        prompt_dir = worktree_path / ".automation"
        prompt_dir.mkdir(parents=True, exist_ok=True)

        prompt = self._settings.prompt_template
        prompt = prompt.replace("{{ issue.identifier }}", issue.identifier)
        prompt = prompt.replace("{{ issue.title }}", issue.title)
        prompt = prompt.replace("{{ issue.description }}", issue.body)
        prompt = prompt.replace("{{ issue.url }}", issue.html_url)
        prompt = prompt.replace("{{ issue.priority }}", "P2")

        (prompt_dir / "issue-prompt.md").write_text(prompt, encoding="utf-8")

    async def _run_agent(self, issue: GitHubIssue, worktree_path: Path) -> None:
        prompt_path = worktree_path / ".automation" / "issue-prompt.md"
        if not self._settings.agent_command:
            raise PipelineError("未配置 AUTOMATION_AGENT_COMMAND，无法自动执行 AI 任务")

        command = self._render_template(
            self._settings.agent_command,
            {
                "issue_number": str(issue.number),
                "issue_title": issue.title,
                "issue_identifier": issue.identifier,
                "issue_url": issue.html_url,
                "issue_body": issue.body,
                "workspace": str(worktree_path),
                "workflow": str(self._settings.workflow_path),
                "prompt": str(prompt_path),
                "branch_name": "",
                "base_branch": self._settings.base_branch,
                "agent_command": self._settings.agent_command,
                "quality_commands": " ; ".join(self._settings.quality_commands),
            },
        )

        await self._run_command(command, cwd=worktree_path)

    async def _run_quality_checks(
        self,
        issue: GitHubIssue,
        worktree_path: Path,
        branch_name: str,
    ) -> list[QualityGateResult]:
        results: list[QualityGateResult] = []

        for command in self._settings.quality_commands:
            result = await self._run_command(command, cwd=worktree_path, check=False)
            results.append(
                QualityGateResult(
                    command=command,
                    exit_code=result.exit_code,
                    output=result.stdout,
                )
            )
            if result.exit_code != 0:
                raise PipelineError(f"质量检查失败: {command}")

        return results

    async def _has_git_changes(self, worktree_path: Path) -> bool:
        result = await self._run_command(
            "git status --porcelain", cwd=worktree_path, check=False
        )
        return bool(result.stdout.strip())

    async def _commit_and_push(
        self,
        issue: GitHubIssue,
        worktree_path: Path,
        branch_name: str,
    ) -> None:
        await self._run_command("git add -A", cwd=worktree_path)

        check = await self._run_command(
            "git diff --cached --quiet", cwd=worktree_path, check=False
        )
        if check.exit_code == 0:
            raise PipelineError("没有可提交改动")

        message = f"fix(issue-{issue.number}): {issue.title}"
        await self._run_command(f"git commit -m {_quote(message)}", cwd=worktree_path)

        skip_push = os.getenv("AUTOMATION_SKIP_GIT_PUSH", "").strip().lower() in {
            "1",
            "true",
            "yes",
        }
        if skip_push:
            logger.warning("AUTOMATION_SKIP_GIT_PUSH enabled; skipping git push step.")
            return

        await self._run_command(f"git push -u origin {branch_name}", cwd=worktree_path)

    def _render_template(self, template: str, context: dict[str, str]) -> str:
        rendered = template
        for key, value in context.items():
            rendered = rendered.replace(f"{{{key}}}", value)
        return rendered

    async def _run_command(
        self,
        command: str,
        cwd: Path,
        check: bool = True,
    ) -> CommandResult:
        if self._settings.dry_run:
            logger.info("[DRY-RUN] command=%s cwd=%s", command, cwd)
            return CommandResult(exit_code=0, stdout="", stderr="")

        result = await asyncio.to_thread(_exec_shell, command, cwd)
        if check and result.exit_code != 0:
            raise PipelineError(
                f"命令执行失败: {command}\n退出码: {result.exit_code}\n输出:\n{result.stdout}"
            )
        return result

    async def _run_hook_command(self, hook_name: str, command: str, cwd: Path) -> None:
        result = await self._run_command(command, cwd=cwd, check=False)
        if result.exit_code == 0:
            return

        strict_hooks = os.getenv("AUTOMATION_HOOKS_STRICT", "false").strip().lower()
        strict = strict_hooks in {"1", "true", "yes"}

        message = (
            f"Hook 执行失败 name={hook_name} exit_code={result.exit_code}\n"
            f"command:\n{command}\n"
            f"output:\n{result.stdout}"
        )
        if strict:
            raise PipelineError(message)

        logger.warning("%s", message)


class CommandResult:
    """命令执行结果。"""

    def __init__(self, exit_code: int, stdout: str, stderr: str) -> None:
        self.exit_code = exit_code
        self.stdout = stdout
        self.stderr = stderr


def _exec_shell(command: str, cwd: Path) -> CommandResult:
    if os.name == "nt":
        use_bash = _should_use_bash_on_windows(command)
        if use_bash:
            bash_executable = _resolve_bash_executable()
            if bash_executable is not None:
                process = subprocess.run(  # noqa: S603
                    [bash_executable, "-lc", command],
                    cwd=str(cwd),
                    capture_output=True,
                    text=True,
                    check=False,
                    encoding="utf-8",
                    errors="replace",
                )
            else:
                powershell_executable = (
                    r"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe"
                )
                process = subprocess.run(  # noqa: S603
                    [powershell_executable, "-NoProfile", "-Command", command],
                    cwd=str(cwd),
                    capture_output=True,
                    text=True,
                    check=False,
                    encoding="utf-8",
                    errors="replace",
                )
        else:
            powershell_executable = (
                r"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe"
            )
            process = subprocess.run(  # noqa: S603
                [powershell_executable, "-NoProfile", "-Command", command],
                cwd=str(cwd),
                capture_output=True,
                text=True,
                check=False,
                encoding="utf-8",
                errors="replace",
            )
    else:
        shell_executable = "/bin/sh"
        process = subprocess.run(  # noqa: S603
            [shell_executable, "-lc", command],
            cwd=str(cwd),
            capture_output=True,
            text=True,
            check=False,
            encoding="utf-8",
            errors="replace",
        )

    output = (process.stdout or "") + (process.stderr or "")
    return CommandResult(
        exit_code=process.returncode, stdout=output, stderr=process.stderr or ""
    )


def _should_use_bash_on_windows(command: str) -> bool:
    forced = os.getenv("AUTOMATION_WINDOWS_SHELL", "").strip().lower()
    if forced in {"bash", "sh"}:
        return True
    if forced in {"powershell", "pwsh"}:
        return False

    # Auto-detect common POSIX shell patterns used in workflow hooks.
    markers = ["if [", "fi", "find . -name", "2>/dev/null", "|| true"]
    lowered = command.lower()
    return any(marker in lowered for marker in markers)


def _resolve_bash_executable() -> str | None:
    explicit = os.getenv("AUTOMATION_BASH_EXE", "").strip()
    if explicit:
        return explicit

    path_bash = shutil.which("bash")
    if path_bash:
        # Ignore Windows WSL launcher (system32\bash.exe), which is often unusable in this context.
        lowered = path_bash.replace("/", "\\").lower()
        if not lowered.endswith("\\windows\\system32\\bash.exe"):
            return path_bash

    git_bash = r"C:\Program Files\Git\bin\bash.exe"
    if Path(git_bash).exists():
        return git_bash

    return None


def _build_pr_body(issue: GitHubIssue, quality_results: list[QualityGateResult]) -> str:
    lines = [
        "## 变更背景",
        f"自动处理 {issue.identifier}: {issue.title}",
        "",
        "## 质量门禁",
    ]

    for result in quality_results:
        status = "PASS" if result.exit_code == 0 else "FAIL"
        lines.append(f"- [{status}] {result.command}")

    lines.extend(
        [
            "",
            "## 关联 Issue",
            f"closes #{issue.number}",
        ]
    )

    return "\n".join(lines)


def _quote(value: str | Path) -> str:
    text = str(value)
    return '"' + text.replace('"', '\\"') + '"'
