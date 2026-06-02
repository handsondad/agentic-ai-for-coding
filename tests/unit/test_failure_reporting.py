"""Tests for failure classification and remediation output."""

from __future__ import annotations

import importlib
import sys
from pathlib import Path

AUTOMATION_DIR = Path(__file__).resolve().parents[2] / ".github" / "automation"
if str(AUTOMATION_DIR) not in sys.path:
    sys.path.insert(0, str(AUTOMATION_DIR))

module = importlib.import_module("failure_reporting")


def test_classify_failure_maps_permission_error() -> None:
    result = module.classify_failure("HTTP 403 Forbidden: token permission denied")
    assert result.category == "network_or_permission"
    assert result.retryable is True


def test_classify_failure_maps_quality_gate_error() -> None:
    result = module.classify_failure("质量检查失败: python -m pytest tests/unit")
    assert result.category == "code_defect"


def test_classify_failure_defaults_to_external_dependency() -> None:
    result = module.classify_failure("unexpected unknown failure in external runner")
    assert result.category == "external_dependency"


def test_render_failure_markdown_contains_required_sections() -> None:
    markdown = module.render_failure_markdown(step="pipeline", raw_error="timeout while fetch")

    assert "自动执行失败（标准化报告）" in markdown
    assert "- 失败步骤: pipeline" in markdown
    assert "- 分类:" in markdown
    assert "- 建议:" in markdown
    assert "```text" in markdown
