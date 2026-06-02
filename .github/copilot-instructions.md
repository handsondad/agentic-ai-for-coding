# GitHub Copilot 编码规范

本文档定义了项目的编码规范，GitHub Copilot 和 Copilot Coding Agent 在生成代码时必须遵循这些规范。

## 项目概述

本项目是一个 AI Agent 应用，基于大语言模型（LLM）构建智能对话和任务执行能力。

## 技术栈

- **语言**：Python 3.12+
- **测试**：pytest, pytest-asyncio, pytest-cov
- **代码质量**：ruff (lint + format), mypy
- **依赖管理**：pyproject.toml + pip

## 代码风格规范

### Python 规范

1. **类型注解**：所有公共函数和方法必须有完整的类型注解
   ```python
   # ✅ 正确
   async def process_message(content: str, context: dict[str, Any]) -> AgentResponse:
       ...

   # ❌ 错误
   async def process_message(content, context):
       ...
   ```

2. **文档字符串**：公共 API 必须有 docstring
   ```python
   def register_tool(name: str, handler: ToolHandler) -> None:
       """注册一个工具到 Agent 工具集。

       Args:
           name: 工具的唯一标识符
           handler: 工具的处理函数

       Raises:
           ValueError: 如果工具名称已存在
       """
   ```

3. **错误处理**：不允许裸露的异常捕获
   ```python
   # ✅ 正确
   try:
       result = await api_call()
   except ApiError as e:
       logger.error("API 调用失败", error=str(e), tool=tool_name)
       raise ToolExecutionError(f"工具执行失败: {e}") from e

   # ❌ 错误
   try:
       result = await api_call()
   except Exception:
       pass
   ```

4. **日志记录**：使用结构化日志，不使用 print
   ```python
   # ✅ 正确
   import logging
   logger = logging.getLogger(__name__)
   logger.info("处理消息", extra={"message_id": msg_id, "user_id": user_id})

   # ❌ 错误
   print(f"处理消息: {msg_id}")
   ```

5. **配置管理**：所有配置从环境变量读取，不硬编码
   ```python
   # ✅ 正确
   import os
   API_KEY = os.environ["OPENAI_API_KEY"]  # 缺失时报错
   MAX_TOKENS = int(os.getenv("MAX_TOKENS", "4096"))  # 有默认值

   # ❌ 错误
   API_KEY = "sk-xxxx..."
   ```

## 架构规范

### 模块划分

```
src/
├── agent/      # Agent 核心逻辑（会话管理、消息处理、状态机）
├── tools/      # 工具定义（每个工具一个文件）
├── memory/     # 记忆和状态持久化
└── api/        # HTTP API 层（路由、中间件、请求验证）
```

**规则**：
- `api/` 只能依赖 `agent/`，不能直接操作 `memory/` 或 `tools/`
- `agent/` 可以依赖 `tools/` 和 `memory/`
- `tools/` 不能依赖 `agent/`（避免循环依赖）
- 禁止跨层的循环依赖

### 异步编程

- 所有 I/O 操作（网络、数据库、文件）必须使用 `async/await`
- 使用 `asyncio.gather()` 并发执行独立的异步操作
- 避免在异步函数中调用阻塞操作，如需要使用 `asyncio.run_in_executor()`

### 数据模型

- 使用 Pydantic v2 定义所有数据结构
- 模型字段必须有类型注解和描述
- 敏感字段使用 `SecretStr` 类型

## 测试规范

### 测试结构

```
tests/
├── unit/           # 单元测试（无外部依赖）
│   ├── test_agent.py
│   ├── test_tools.py
│   └── test_memory.py
├── integration/    # 集成测试（可以有网络/DB依赖，需要 mock）
│   └── test_api.py
└── conftest.py     # 共享 fixtures
```

### 测试编写规范

1. **测试命名**：`test_<被测函数>_<场景描述>`
   ```python
   def test_process_message_returns_response_on_success(): ...
   def test_process_message_raises_on_invalid_input(): ...
   ```

2. **覆盖率要求**：核心业务逻辑覆盖率 > 80%

3. **Mock 策略**：
   - 单元测试必须 mock 所有外部依赖（LLM API、数据库等）
   - 集成测试使用真实组件，但 mock 第三方 API

4. **测试独立性**：每个测试必须独立，不依赖执行顺序

## 安全规范

1. **输入验证**：所有来自外部的数据（API 请求、用户输入）必须在入口处验证
2. **无敏感信息泄露**：日志中不记录 API Keys、密码、用户私密内容
3. **SQL 安全**：如果使用数据库，必须使用参数化查询，不拼接 SQL
4. **依赖安全**：新增依赖前检查是否有已知漏洞

## Git 提交规范

使用 [Conventional Commits](https://www.conventionalcommits.org/zh-hans/)：

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

**type 类型**：
- `feat`: 新功能
- `fix`: Bug 修复
- `refactor`: 代码重构（不改变功能）
- `test`: 添加或修改测试
- `docs`: 文档更新
- `chore`: 工程任务（依赖更新、配置修改等）

**示例**：
```
feat(agent): 添加多轮对话历史管理

实现基于滑动窗口的对话历史截断机制，避免超出 token 限制。

Closes #42
```

## 禁止事项

- ❌ 不在代码中存储 API Keys 或密码
- ❌ 不提交 `.env` 文件到版本库
- ❌ 不使用 `eval()` 或动态执行用户输入的代码
- ❌ 不绕过类型检查（避免过多使用 `Any` 和 `# type: ignore`）
- ❌ 不在生产代码中使用 `print()` 调试
- ❌ 不创建超过 500 行的单文件（应拆分）
