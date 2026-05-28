"""API 集成测试。"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from src.api.routes import app


@pytest.fixture
def client() -> TestClient:
    """创建 FastAPI 测试客户端。"""
    return TestClient(app)


class TestHealthCheck:
    """健康检查端点测试。"""

    def test_health_check_returns_ok(self, client: TestClient) -> None:
        """健康检查应该返回 200 和 ok 状态。"""
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "active_sessions" in data


class TestChatEndpoint:
    """聊天端点集成测试。"""

    def test_chat_returns_response(self, client: TestClient) -> None:
        """POST /api/v1/chat 应该返回 Agent 响应。"""
        response = client.post(
            "/api/v1/chat",
            json={
                "session_id": "integration-test-1",
                "message": "你好",
                "stream": False,
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["session_id"] == "integration-test-1"
        assert len(data["response"]) > 0

    def test_chat_empty_session_id_returns_400(self, client: TestClient) -> None:
        """空的 session_id 应该返回 400 错误。"""
        response = client.post(
            "/api/v1/chat",
            json={
                "session_id": "",
                "message": "你好",
                "stream": False,
            },
        )

        assert response.status_code == 400

    def test_chat_empty_message_returns_400(self, client: TestClient) -> None:
        """空消息应该返回 400 错误。"""
        response = client.post(
            "/api/v1/chat",
            json={
                "session_id": "session-1",
                "message": "",
                "stream": False,
            },
        )

        assert response.status_code == 400


class TestSessionEndpoint:
    """会话管理端点测试。"""

    def test_terminate_existing_session(self, client: TestClient) -> None:
        """终止存在的会话应该返回 terminated=true。"""
        # 先创建一个会话
        client.post(
            "/api/v1/chat",
            json={"session_id": "to-delete", "message": "你好", "stream": False},
        )

        # 再终止它
        response = client.delete("/api/v1/sessions/to-delete")
        assert response.status_code == 200
        assert response.json()["terminated"] is True

    def test_terminate_nonexistent_session(self, client: TestClient) -> None:
        """终止不存在的会话应该返回 terminated=false。"""
        response = client.delete("/api/v1/sessions/nonexistent-session-xyz")
        assert response.status_code == 200
        assert response.json()["terminated"] is False
