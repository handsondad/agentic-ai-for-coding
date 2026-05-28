.PHONY: help setup dev test test-unit test-integration lint format build clean

# 默认目标：显示帮助
help:
	@echo "AI Agent 项目开发命令"
	@echo ""
	@echo "环境管理："
	@echo "  make setup              安装开发依赖"
	@echo "  make clean              清理构建产物和缓存"
	@echo ""
	@echo "开发："
	@echo "  make dev                启动本地开发服务器（热重载）"
	@echo ""
	@echo "测试："
	@echo "  make test               运行所有测试"
	@echo "  make test-unit          只运行单元测试"
	@echo "  make test-integration   只运行集成测试"
	@echo "  make test-cov           运行测试并生成覆盖率报告"
	@echo ""
	@echo "代码质量："
	@echo "  make lint               运行代码检查（ruff + mypy）"
	@echo "  make format             自动格式化代码"
	@echo ""
	@echo "构建："
	@echo "  make build              构建 Python 包"
	@echo "  make docker-build       构建 Docker 镜像"
	@echo ""
	@echo "发布："
	@echo "  make release VERSION=v1.0.0   打版本标签并推送"

# ─────────────────────────────────────────────
# 环境管理
# ─────────────────────────────────────────────

setup:
	pip install -e ".[dev]" 2>/dev/null || \
	  (pip install -r requirements-dev.txt 2>/dev/null || \
	  pip install pytest pytest-asyncio pytest-cov ruff mypy)
	@echo "✅ 开发环境安装完成"

clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	rm -rf dist/ build/ coverage.xml htmlcov/
	@echo "✅ 清理完成"

# ─────────────────────────────────────────────
# 开发
# ─────────────────────────────────────────────

dev:
	@echo "🚀 启动开发服务器..."
	python -m uvicorn src.api.routes:app --reload --host 0.0.0.0 --port 8000

# ─────────────────────────────────────────────
# 测试
# ─────────────────────────────────────────────

test:
	pytest tests/ -v
	@echo "✅ 所有测试通过"

test-unit:
	pytest tests/unit/ -v
	@echo "✅ 单元测试通过"

test-integration:
	pytest tests/integration/ -v --timeout=60
	@echo "✅ 集成测试通过"

test-cov:
	pytest tests/ -v \
	  --cov=src \
	  --cov-report=term-missing \
	  --cov-report=html:htmlcov \
	  --cov-report=xml:coverage.xml
	@echo "✅ 覆盖率报告生成完成（htmlcov/index.html）"

# ─────────────────────────────────────────────
# 代码质量
# ─────────────────────────────────────────────

lint:
	@echo "🔍 运行 Ruff 检查..."
	ruff check src/ tests/
	@echo "🔍 检查代码格式..."
	ruff format --check src/ tests/
	@echo "🔍 运行 Mypy 类型检查..."
	mypy src/ --ignore-missing-imports
	@echo "✅ 代码检查通过"

format:
	@echo "✏️  格式化代码..."
	ruff format src/ tests/
	ruff check --fix src/ tests/
	@echo "✅ 格式化完成"

# ─────────────────────────────────────────────
# 构建
# ─────────────────────────────────────────────

build:
	pip install build
	python -m build
	@echo "✅ 构建完成（dist/ 目录）"

docker-build:
	docker build -t ai-agent:latest .
	@echo "✅ Docker 镜像构建完成"

# ─────────────────────────────────────────────
# 发布
# ─────────────────────────────────────────────

release:
	@if [ -z "$(VERSION)" ]; then \
	  echo "❌ 请指定版本号：make release VERSION=v1.0.0"; \
	  exit 1; \
	fi
	@echo "🚀 创建发布标签 $(VERSION)..."
	git tag -a $(VERSION) -m "Release $(VERSION)"
	git push origin $(VERSION)
	@echo "✅ 标签已推送，GitHub Actions 将自动完成发布流程"
