"""Failure classification and remediation reporting helpers."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class FailureClassification:
    """Standard failure classification output."""

    category: str
    reason: str
    suggestion: str
    retryable: bool


def classify_failure(message: str) -> FailureClassification:
    """Classify failure message into standard categories."""
    lowered = message.lower()

    if any(token in lowered for token in ["403", "forbidden", "permission", "token", "auth"]):
        return FailureClassification(
            category="network_or_permission",
            reason="认证或权限不足，导致 GitHub 写操作失败。",
            suggestion=(
                "检查 GITHUB_TOKEN 权限（Issues/Pull requests/Contents 读写）并确认当前登录态。"
            ),
            retryable=True,
        )

    network_tokens = ["timeout", "timed out", "connection", "ssl", "certificate"]
    if any(token in lowered for token in network_tokens):
        return FailureClassification(
            category="environment_blocker",
            reason="网络或 TLS 环境异常导致外部连接失败。",
            suggestion="检查代理、证书链和网络连通性后重试。",
            retryable=True,
        )

    env_tokens = ["未配置", "missing", "not found", "environment variable"]
    if any(token in lowered for token in env_tokens):
        return FailureClassification(
            category="environment_blocker",
            reason="运行环境缺少必要配置或文件。",
            suggestion="补齐缺失环境变量/配置文件后重新执行。",
            retryable=True,
        )

    if any(token in lowered for token in ["quality", "lint", "mypy", "pytest", "test", "格式"]):
        return FailureClassification(
            category="code_defect",
            reason="代码质量门禁未通过。",
            suggestion="根据失败日志修复代码或测试，并重新执行质量门禁。",
            retryable=True,
        )

    if any(token in lowered for token in ["acceptance", "需求", "scope", "冲突", "ambiguous"]):
        return FailureClassification(
            category="requirements_gap",
            reason="需求信息不足或存在冲突，无法继续自动执行。",
            suggestion="补充验收标准或澄清需求边界后重试。",
            retryable=False,
        )

    return FailureClassification(
        category="external_dependency",
        reason="未归类异常，可能来自外部依赖或执行环境。",
        suggestion="查看完整日志，定位首个报错步骤并按最小变更修复。",
        retryable=True,
    )


def render_failure_markdown(step: str, raw_error: str) -> str:
    """Render standardized markdown failure report for issue/PR comments."""
    classification = classify_failure(raw_error)
    lines = [
        "自动执行失败（标准化报告）",
        "",
        f"- 失败步骤: {step}",
        f"- 分类: {classification.category}",
        f"- 是否可重试: {'是' if classification.retryable else '否'}",
        f"- 原因: {classification.reason}",
        f"- 建议: {classification.suggestion}",
        "",
        "原始错误摘要:",
        "```text",
        raw_error.strip(),
        "```",
    ]
    return "\n".join(lines)
