"""AI Agent 应用包。

本模块是 AI Agent 应用的根包，导出核心组件供外部使用。
"""

from src.agent.core import AgentCore
from src.agent.session import AgentSession, SessionStatus

__all__ = ["AgentCore", "AgentSession", "SessionStatus"]
__version__ = "0.1.0"
