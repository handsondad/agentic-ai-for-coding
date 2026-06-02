"""Single-issue preparation workflow tests."""

from __future__ import annotations

import importlib.util
import os
import sys
from pathlib import Path


def _load_module() -> object:
    script_path = (
        Path(__file__).resolve().parents[2]
        / ".github"
        / "automation"
        / "scripts"
        / "prepare-single-issue.py"
    )
    spec = importlib.util.spec_from_file_location("prepare_single_issue", script_path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_load_local_issue_reads_front_matter(tmp_path: Path) -> None:
    module = _load_module()

    issue_file = tmp_path / "single-issue.md"
    issue_file.write_text(
        """---
title: "feat: 单 issue 手工工作流"
labels:
  - feature
github_issue_number: "12"
github_issue_url: "https://github.com/octo/demo/issues/12"
---

## 背景

这是一个本地 issue 文件。
""",
        encoding="utf-8",
    )

    issue = module._load_local_issue(issue_file)

    assert issue.number == 12
    assert issue.title == "feat: 单 issue 手工工作流"
    assert issue.html_url == "https://github.com/octo/demo/issues/12"
    assert issue.labels == ["feature"]
    assert "本地 issue 文件" in issue.body


def test_load_local_issue_falls_back_to_heading(tmp_path: Path) -> None:
    module = _load_module()

    issue_file = tmp_path / "my-local-issue.md"
    issue_file.write_text(
        """# 直接从本地文件开始

这里没有 front matter。
""",
        encoding="utf-8",
    )

    issue = module._load_local_issue(issue_file)

    assert issue.number == 0
    assert issue.title == "直接从本地文件开始"
    assert issue.html_url == str(issue_file)


def test_load_windows_user_env_fallback_reads_missing_values(monkeypatch: object) -> None:
    module = _load_module()

    monkeypatch.setattr(module.os, "name", "nt")
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    monkeypatch.setenv("GITHUB_REPOSITORY", "existing/repo")

    fake_winreg = type(
        "FakeWinReg",
        (),
        {
            "HKEY_CURRENT_USER": object(),
            "OpenKey": staticmethod(lambda root, path: _FakeKey()),
            "QueryValueEx": staticmethod(_fake_query_value_ex),
        },
    )
    monkeypatch.setitem(sys.modules, "winreg", fake_winreg)

    module._load_windows_user_env_fallback("GITHUB_TOKEN", "GITHUB_REPOSITORY")

    assert os.environ["GITHUB_TOKEN"].startswith("user-")
    assert os.environ["GITHUB_REPOSITORY"] == "existing/repo"


class _FakeKey:
    def __enter__(self) -> object:
        return self

    def __exit__(self, exc_type: object, exc: object, tb: object) -> bool:
        return False


def _fake_query_value_ex(_key: object, name: str) -> tuple[str, int]:
    values = {
        "GITHUB_TOKEN": "user-token",
        "GITHUB_REPOSITORY": "user/repo",
    }
    return values[name], 1
