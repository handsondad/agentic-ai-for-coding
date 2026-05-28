"""API 路由模块。

定义 HTTP API 端点，使用 FastAPI 框架。
"""

from __future__ import annotations

import logging
from collections.abc import AsyncIterator

from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from src.agent.core import AgentCore

logger = logging.getLogger(__name__)

app = FastAPI(
    title="AI Agent API",
    description="AI Agent 应用的 HTTP API 接口",
    version="0.1.0",
)

# 全局 Agent 实例（生产环境可使用依赖注入管理）
_agent = AgentCore()


class ChatRequest(BaseModel):
    """聊天请求模型。"""

    session_id: str
    message: str
    stream: bool = True


class ChatResponse(BaseModel):
    """非流式聊天响应模型。"""

    session_id: str
    response: str


@app.get("/health")
async def health_check() -> dict[str, str]:
    """健康检查端点。"""
    return {"status": "ok", "active_sessions": str(_agent.active_session_count)}


@app.post("/api/v1/chat", response_model=None)
async def chat(request: ChatRequest) -> StreamingResponse | ChatResponse:
    """处理聊天消息。

    支持流式和非流式两种响应模式。

    Args:
        request: 聊天请求，包含 session_id、message 和 stream 标志

    Returns:
        流式响应（stream=True）或完整响应（stream=False）

    Raises:
        HTTPException: 如果请求参数无效或处理出错
    """
    if not request.session_id or not request.session_id.strip():
        raise HTTPException(status_code=400, detail="session_id 不能为空")

    if not request.message or not request.message.strip():
        raise HTTPException(status_code=400, detail="message 不能为空")

    logger.info(
        "收到聊天请求",
        extra={
            "session_id": request.session_id,
            "stream": request.stream,
            "message_length": len(request.message),
        },
    )

    try:
        if request.stream:
            return StreamingResponse(
                _stream_chat(request.session_id, request.message),
                media_type="text/event-stream",
            )
        else:
            chunks = []
            async for chunk in _agent.chat(request.session_id, request.message):
                chunks.append(chunk)
            return ChatResponse(
                session_id=request.session_id,
                response="".join(chunks),
            )

    except RuntimeError as e:
        raise HTTPException(status_code=409, detail=str(e)) from e
    except Exception as e:
        logger.error(
            "聊天请求处理失败",
            extra={"session_id": request.session_id, "error": str(e)},
        )
        raise HTTPException(status_code=500, detail="内部服务器错误") from e


async def _stream_chat(session_id: str, message: str) -> AsyncIterator[str]:
    """生成流式响应的异步迭代器。"""
    async for chunk in _agent.chat(session_id, message):
        yield f"data: {chunk}\n\n"
    yield "data: [DONE]\n\n"


@app.delete("/api/v1/sessions/{session_id}")
async def terminate_session(session_id: str) -> dict[str, bool]:
    """终止指定会话。

    Args:
        session_id: 要终止的会话 ID

    Returns:
        {"terminated": true} 如果会话存在并被终止
        {"terminated": false} 如果会话不存在
    """
    terminated = _agent.terminate_session(session_id)
    return {"terminated": terminated}
