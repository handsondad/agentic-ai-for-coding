"""Workspace hook helper tests."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest


def _load_module() -> object:
    script_path = (
        Path(__file__).resolve().parents[2]
        / ".github"
        / "automation"
        / "scripts"
        / "workspace-hooks.py"
    )
    spec = importlib.util.spec_from_file_location("workspace_hooks", script_path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_run_after_create_installs_existing_dependencies(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    module = _load_module()
    (tmp_path / "requirements.txt").write_text("pytest\n", encoding="utf-8")
    (tmp_path / "pyproject.toml").write_text("[project]\nname='demo'\n", encoding="utf-8")

    calls: list[tuple[list[str], str]] = []

    def fake_run(**kwargs: object) -> None:
        raise AssertionError("unexpected keyword-only call")

    def fake_subprocess_run(
        command: list[str],
        cwd: str,
        check: bool,
        text: bool,
        encoding: str,
        errors: str,
    ) -> None:
        calls.append((command, cwd))
        assert check is True
        assert text is True
        assert encoding == "utf-8"
        assert errors == "replace"

    monkeypatch.setattr(module.subprocess, "run", fake_subprocess_run)

    module.run_after_create(tmp_path)

    assert calls == [
        ([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], str(tmp_path)),
        ([sys.executable, "-m", "pip", "install", "-e", ".[dev]"], str(tmp_path)),
    ]
    assert "工作空间初始化完成" in capsys.readouterr().out


def test_run_before_run_fetches_requested_branch(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    module = _load_module()
    calls: list[list[str]] = []

    def fake_subprocess_run(
        command: list[str],
        cwd: str,
        check: bool,
        text: bool,
        encoding: str,
        errors: str,
    ) -> None:
        calls.append(command)
        assert cwd == str(tmp_path)
        assert check is True
        assert text is True
        assert encoding == "utf-8"
        assert errors == "replace"

    monkeypatch.setattr(module.subprocess, "run", fake_subprocess_run)

    module.run_before_run(tmp_path, base_branch="release")

    assert calls == [["git", "fetch", "origin", "release"]]
    assert "代码同步完成" in capsys.readouterr().out


def test_run_after_run_removes_python_cache_files(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    module = _load_module()
    pycache_dir = tmp_path / "pkg" / "__pycache__"
    pycache_dir.mkdir(parents=True)
    (pycache_dir / "module.cpython-312.pyc").write_bytes(b"pyc")
    (tmp_path / "top.pyc").write_bytes(b"pyc")

    module.run_after_run(tmp_path)

    assert not pycache_dir.exists()
    assert not (tmp_path / "top.pyc").exists()
    assert "清理完成" in capsys.readouterr().out
