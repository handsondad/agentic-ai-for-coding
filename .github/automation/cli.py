"""本地调度 CLI。"""

from __future__ import annotations

import argparse
import asyncio
import logging
from pathlib import Path

try:
    from .service import AutomationService
    from .workflow import load_runtime_settings
except ImportError:
    from service import AutomationService
    from workflow import load_runtime_settings


def main() -> None:
    """CLI 入口。"""
    parser = argparse.ArgumentParser(description="本地 issue 自动执行器")
    parser.add_argument(
        "--workflow",
        default="WORKFLOW.md",
        help="WORKFLOW.md 路径（默认: WORKFLOW.md）",
    )
    parser.add_argument(
        "--once",
        action="store_true",
        help="只轮询执行一次（适合 Cron/计划任务）",
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="日志级别",
    )

    args = parser.parse_args()

    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )

    workflow_path = Path(args.workflow).resolve()
    settings = load_runtime_settings(workflow_path)

    service = AutomationService(settings)
    if args.once:
        asyncio.run(service.run_once())
    else:
        asyncio.run(service.run_forever())


if __name__ == "__main__":
    main()
