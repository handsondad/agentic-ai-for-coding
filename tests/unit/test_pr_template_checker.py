"""Tests for PR template completeness checker."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest


def _load_module() -> object:
    script_path = (
        Path(__file__).resolve().parents[2]
        / ".github"
        / "automation"
        / "scripts"
        / "check-pr-template.py"
    )
    spec = importlib.util.spec_from_file_location("check_pr_template", script_path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_validate_pr_body_passes_with_required_sections() -> None:
    module = _load_module()
    body = """
## 背景
说明

## 变更摘要
说明

## 变更详情
- A

## 测试计划
- [x] 已执行: unit
- [ ] 未执行: integration

## 审查重点
关注点
""".strip()

    ok, messages = module.validate_pr_body(body)
    assert ok is True
    assert messages == []


def test_validate_pr_body_fails_missing_section() -> None:
    module = _load_module()
    body = "## 背景\nonly"

    ok, messages = module.validate_pr_body(body)
    assert ok is False
    assert any("缺少必填章节" in item for item in messages)


def test_validate_pr_body_fails_placeholder_comment() -> None:
    module = _load_module()
    body = """
## 背景
<!-- TODO -->

## 变更摘要
ok

## 变更详情
ok

## 测试计划
- [x] 已执行
- [ ] 未执行

## 审查重点
ok
""".strip()

    ok, messages = module.validate_pr_body(body)
    assert ok is False
    assert "模板注释" in "\n".join(messages)


def test_load_pr_body_from_event_path(tmp_path: Path) -> None:
    module = _load_module()
    payload = {
        "pull_request": {
            "body": "## 背景\n内容",
        }
    }
    event_path = tmp_path / "event.json"
    event_path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")

    args = module.parse_args.__globals__["argparse"].Namespace(
        body_text="",
        body_file="",
        event_path=str(event_path),
    )

    assert module.load_pr_body(args) == "## 背景\n内容"


def test_load_pr_body_requires_source() -> None:
    module = _load_module()
    args = module.parse_args.__globals__["argparse"].Namespace(
        body_text="",
        body_file="",
        event_path="",
    )

    with pytest.raises(ValueError, match="Provide one of"):
        module.load_pr_body(args)
