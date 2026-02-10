from google.adk.apps import App

from .workflow import root_agent

app = App(name="SE_workflow_test", root_agent=root_agent)

__all__ = ["root_agent", "app"]
