"""Automation GitHub client preflight tests."""

from __future__ import annotations

import importlib
import subprocess
import sys
from pathlib import Path

import pytest

AUTOMATION_DIR = Path(__file__).resolve().parents[2] / ".github" / "automation"
if str(AUTOMATION_DIR) not in sys.path:
    sys.path.insert(0, str(AUTOMATION_DIR))

models_module = importlib.import_module("models")
client_module = importlib.import_module("github_client")

GitHubRepo = models_module.GitHubRepo
GitHubClient = client_module.GitHubClient


def _completed(returncode: int, stdout: str = "", stderr: str = "") -> subprocess.CompletedProcess[str]:
    return subprocess.CompletedProcess(args=["gh"], returncode=returncode, stdout=stdout, stderr=stderr)


def test_init_raises_when_gh_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(client_module.shutil, "which", lambda _: None)

    with pytest.raises(RuntimeError, match="gh CLI not found"):
        GitHubClient(token="", repo=GitHubRepo(owner="octo", name="demo"))


def test_init_raises_when_not_logged_in_without_token(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(client_module.shutil, "which", lambda _: "C:/tools/gh.exe")
    monkeypatch.setattr(
        client_module.subprocess,
        "run",
        lambda *args, **kwargs: _completed(1, "", "You are not logged into any GitHub hosts"),
    )

    with pytest.raises(RuntimeError, match="gh auth status failed"):
        GitHubClient(token="", repo=GitHubRepo(owner="octo", name="demo"))


def test_init_skips_auth_status_when_token_present(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(client_module.shutil, "which", lambda _: "C:/tools/gh.exe")

    calls: list[list[str]] = []

    def fake_run(cmd: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        calls.append(cmd)
        return _completed(0, "ok", "")

    monkeypatch.setattr(client_module.subprocess, "run", fake_run)

    GitHubClient(token="ghp_xxx", repo=GitHubRepo(owner="octo", name="demo"))

    assert calls == []
