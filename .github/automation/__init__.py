"""本地自动编排模块。"""

try:
    from .service import AutomationService
    from .workflow import WorkflowParseError, load_runtime_settings
except ImportError:
    from service import AutomationService
    from workflow import WorkflowParseError, load_runtime_settings

__all__ = ["AutomationService", "WorkflowParseError", "load_runtime_settings"]
