"""WORKFLOW 解析测试。"""

from __future__ import annotations

import importlib
import sys
from pathlib import Path

import pytest

AUTOMATION_DIR = Path(__file__).resolve().parents[2] / ".github" / "automation"
if str(AUTOMATION_DIR) not in sys.path:
    sys.path.insert(0, str(AUTOMATION_DIR))

workflow_module = importlib.import_module("workflow")
WorkflowParseError = workflow_module.WorkflowParseError
load_runtime_settings = workflow_module.load_runtime_settings
parse_workflow = workflow_module.parse_workflow


def test_parse_workflow_reads_front_matter_and_prompt(tmp_path: Path) -> None:
    """应正确解析 YAML front matter 与模板正文。"""
    workflow = tmp_path / "WORKFLOW.md"
    workflow.write_text(
        """---
tracker:
  kind: github
  api_key: token
  repo: owner/repo
---
hello {{ issue.title }}
""",
        encoding="utf-8",
    )

    config, prompt = parse_workflow(workflow)

    assert config["tracker"]["kind"] == "github"
    assert "{{ issue.title }}" in prompt


def test_load_runtime_settings_resolves_env_values(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """应支持从环境变量解析 token 与 repo。"""
    workflow = tmp_path / "WORKFLOW.md"
    workflow.write_text(
        """---
tracker:
  kind: github
  api_key: $GITHUB_TOKEN
  repo: $GITHUB_REPOSITORY
polling:
  interval_ms: 15000
agent:
  max_concurrent_agents: 2
workspace:
  root: $AUTOMATION_WORKSPACE_ROOT
---
prompt body
""",
        encoding="utf-8",
    )

    expected_github_token = "ghp_test_value"  # noqa: S105
    monkeypatch.setenv("GITHUB_TOKEN", expected_github_token)
    monkeypatch.setenv("GITHUB_REPOSITORY", "octo/demo")
    monkeypatch.setenv("AUTOMATION_WORKSPACE_ROOT", str(tmp_path / "worktrees"))

    settings = load_runtime_settings(workflow)

    assert settings.github_token == expected_github_token
    assert settings.github_repo.full_name == "octo/demo"
    assert settings.poll_interval_ms == 15000
    assert settings.max_concurrent_agents == 2
    assert settings.workspace_root == (tmp_path / "worktrees").resolve()


def test_load_runtime_settings_raises_when_env_missing(tmp_path: Path) -> None:
    """缺失必需环境变量时应抛错。"""
    workflow = tmp_path / "WORKFLOW.md"
    workflow.write_text(
        """---
tracker:
  kind: github
  api_key: $MISSING_TOKEN
  repo: owner/repo
---
prompt
""",
        encoding="utf-8",
    )

    with pytest.raises(WorkflowParseError, match="环境变量未设置"):
        load_runtime_settings(workflow)


def test_load_runtime_settings_loads_skill_commands(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """应从 skills 文件读取步骤命令。"""
    workflow = tmp_path / "WORKFLOW.md"
    workflow.write_text(
        """---
tracker:
  kind: github
  api_key: $GITHUB_TOKEN
  repo: $GITHUB_REPOSITORY
---
prompt
""",
        encoding="utf-8",
    )

    skills_file = tmp_path / "skills.yaml"
    skills_file.write_text(
        """skills:
  run_agent:
    command: "python run_agent.py --issue {issue_number}"
  quality_gate:
    command: "make lint ; make test"
""",
        encoding="utf-8",
    )

    monkeypatch.setenv("GITHUB_TOKEN", "ghp_test_value")
    monkeypatch.setenv("GITHUB_REPOSITORY", "octo/demo")
    monkeypatch.setenv("AUTOMATION_REPO_ROOT", str(tmp_path))
    monkeypatch.setenv("AUTOMATION_SKILLS_FILE", str(skills_file))
    monkeypatch.setenv("AUTOMATION_USE_SKILLS", "true")

    settings = load_runtime_settings(workflow)

    assert settings.use_skills is True
    assert settings.skill_commands["run_agent"] == "python run_agent.py --issue {issue_number}"
    assert settings.skill_commands["quality_gate"] == "make lint ; make test"


def test_load_runtime_settings_disables_skills_with_env(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """禁用 skills 时应忽略 skills 文件。"""
    workflow = tmp_path / "WORKFLOW.md"
    workflow.write_text(
        """---
tracker:
  kind: github
  api_key: $GITHUB_TOKEN
  repo: $GITHUB_REPOSITORY
---
prompt
""",
        encoding="utf-8",
    )

    skills_file = tmp_path / "skills.yaml"
    skills_file.write_text(
        """skills:
  run_agent:
    command: "python run_agent.py"
""",
        encoding="utf-8",
    )

    monkeypatch.setenv("GITHUB_TOKEN", "ghp_test_value")
    monkeypatch.setenv("GITHUB_REPOSITORY", "octo/demo")
    monkeypatch.setenv("AUTOMATION_REPO_ROOT", str(tmp_path))
    monkeypatch.setenv("AUTOMATION_SKILLS_FILE", str(skills_file))
    monkeypatch.setenv("AUTOMATION_USE_SKILLS", "false")

    settings = load_runtime_settings(workflow)

    assert settings.use_skills is False
    assert settings.skill_commands == {}


def test_load_runtime_settings_renders_hook_templates(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """应将 hook 模板中的仓库路径与基线分支渲染为运行时值。"""
    workflow = tmp_path / "WORKFLOW.md"
    workflow.write_text(
        """---
tracker:
  kind: github
  api_key: $GITHUB_TOKEN
  repo: $GITHUB_REPOSITORY
hooks:
  after_create: 'python "{{ repo_root }}/tool.py" after-create'
  before_run: 'python "{{ repo_root }}/tool.py" before-run --base-branch "{{ base_branch }}"'
---
prompt
""",
        encoding="utf-8",
    )

    monkeypatch.setenv("GITHUB_TOKEN", "ghp_test_value")
    monkeypatch.setenv("GITHUB_REPOSITORY", "octo/demo")
    monkeypatch.setenv("AUTOMATION_REPO_ROOT", str(tmp_path / "repo"))
    monkeypatch.setenv("GITHUB_BASE_BRANCH", "release")

    settings = load_runtime_settings(workflow)

    expected_repo_root = (tmp_path / "repo").resolve().as_posix()
    assert settings.hooks.after_create == f'python "{expected_repo_root}/tool.py" after-create'
    assert settings.hooks.before_run == (
        f'python "{expected_repo_root}/tool.py" before-run --base-branch "release"'
    )
