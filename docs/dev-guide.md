# 开发者指南

本文档面向参与本项目开发的工程师，包括本地环境搭建、开发流程、调试技巧等实用信息。

## 本地环境搭建

### 前置条件

- Python 3.12
- Git
- Docker（可选，用于集成测试）

### 快速开始

```bash
# 1. 克隆仓库
git clone <your-repo-url>
cd <your-repo>

# 2. 创建虚拟环境
python -m venv .venv
source .venv/bin/activate  # macOS/Linux
# 或 .venv\Scripts\activate  # Windows

# 3. 安装开发依赖
make setup
# 等效于：pip install -e ".[dev]"

# 4. 配置环境变量
cp .env.example .env
# 编辑 .env 填入你的 API Keys 等配置

# 5. 验证环境
make test
```

### 环境变量说明

| 变量名 | 必填 | 说明 |
|--------|------|------|
| `OPENAI_API_KEY` | ✅ | OpenAI API Key |
| `OPENAI_BASE_URL` | ❌ | 自定义 API 端点（默认：OpenAI 官方） |
| `LOG_LEVEL` | ❌ | 日志级别（默认：INFO） |
| `MAX_CONCURRENT_SESSIONS` | ❌ | 最大并发会话数（默认：10） |

## 日常开发命令

```bash
# 运行所有测试
make test

# 只运行单元测试（快速）
make test-unit

# 运行集成测试
make test-integration

# 代码 lint 检查
make lint

# 自动格式化代码
make format

# 启动本地开发服务器
make dev

# 查看所有可用命令
make help
```

## 开发工作流

### 使用 AI Agent 实现功能（推荐）

1. 创建 Issue（使用功能需求或开发任务模板）
2. 确保 Issue 描述足够详细（验收标准明确）
3. 给 Issue 打上 `copilot` 标签
4. Copilot Agent 自动创建分支并实现功能
5. 审查 PR，提供反馈或直接合并

### 手动开发流程

1. 从 Issue 创建分支：
   ```bash
   git checkout -b feat/42-add-streaming-response
   ```

2. 开发时保持小步提交，使用 Conventional Commits 格式：
   ```bash
   git commit -m "feat(agent): 添加流式响应支持"
   ```

3. 推送并创建 PR：
   ```bash
   git push origin feat/42-add-streaming-response
   # 在 GitHub 上创建 PR，使用 PR 模板
   ```

4. 等待 CI 通过，请求 Code Review

## 代码组织原则

### 文件大小限制

- 单个文件不超过 500 行
- 如果超过，考虑拆分为多个模块

### 模块依赖规则

```
api/ → agent/ → tools/
              → memory/

# 禁止的依赖方向
tools/ → agent/  # ❌ 循环依赖
memory/ → agent/ # ❌ 循环依赖
```

### 添加新工具

1. 在 `src/tools/` 下创建新文件 `my_tool.py`
2. 使用 `@tool_registry.register` 装饰器注册
3. 在 `src/tools/__init__.py` 中导入
4. 在 `tests/unit/test_tools.py` 中添加测试

```python
# src/tools/my_tool.py
from src.tools.registry import tool_registry
from pydantic import BaseModel

class MyToolParams(BaseModel):
    query: str

@tool_registry.register(
    name="my_tool",
    description="工具的功能描述",
    parameters=MyToolParams
)
async def my_tool(params: MyToolParams) -> dict:
    # 实现工具逻辑
    return {"result": "..."}
```

## 测试策略

### 测试层次

```
单元测试（快，隔离）
  └── 测试单个函数/类的逻辑
  └── 所有外部依赖都 Mock
  └── 运行时间：< 1ms/测试

集成测试（慢，真实）
  └── 测试多个组件的协作
  └── 可以有真实的数据库连接
  └── 第三方 API 需要 Mock
  └── 运行时间：< 5s/测试
```

### Mock 策略

```python
# 推荐：使用 pytest fixtures 管理 Mock
@pytest.fixture
def mock_openai_client(mocker):
    return mocker.patch("src.agent.core.openai.AsyncOpenAI")

def test_agent_sends_correct_prompt(mock_openai_client):
    # 使用 mock 进行测试
    ...
```

### 测试覆盖率要求

| 模块 | 最低覆盖率 |
|------|----------|
| `src/agent/` | 85% |
| `src/tools/` | 90% |
| `src/api/` | 80% |
| `src/memory/` | 80% |

## 调试技巧

### 本地调试 API

```bash
# 启动调试模式（热重载）
make dev

# 访问 API 文档
open http://localhost:8000/docs
```

### 查看日志

```bash
# 开发时使用详细日志
LOG_LEVEL=DEBUG make dev

# 过滤特定模块日志
LOG_LEVEL=DEBUG make dev 2>&1 | grep "agent.core"
```

### 常见问题排查

**Q: 测试失败，提示找不到模块**
```bash
# 确保设置了 PYTHONPATH
PYTHONPATH=. pytest tests/
```

**Q: ruff 格式检查失败**
```bash
# 自动修复格式问题
make format
```

**Q: mypy 类型检查报错**
```bash
# 查看详细的类型错误
mypy src/ --show-error-codes
```

## 发布流程

参见 [README.md 中的发布策略](../README.md#分支与发布策略)。

```bash
# 打版本标签触发自动发布
git tag -a v1.0.0 -m "Release v1.0.0: 首次正式版本"
git push origin v1.0.0
```
