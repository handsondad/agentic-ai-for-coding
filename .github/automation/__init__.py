"""本地自动编排模块。"""

try:
    from .celery_dispatcher import CeleryDispatchService
    from .workflow import WorkflowParseError, load_runtime_settings
except ImportError:
    from celery_dispatcher import CeleryDispatchService
    from workflow import WorkflowParseError, load_runtime_settings

__all__ = ["CeleryDispatchService", "WorkflowParseError", "load_runtime_settings"]
