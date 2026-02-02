from google.adk.apps import App

from .telemetry import ActionLoggingPlugin, create_sink
from .workflow import root_agent

sink = create_sink(app_name="SE_workflow_test")
app = App(
    name="SE_workflow_test",
    root_agent=root_agent,
    plugins=[ActionLoggingPlugin(sink=sink)],
)

__all__ = ["root_agent", "app"]
