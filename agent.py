import logging
import os

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

if os.getenv("AUTO_CONFIGURE_DATABRICKS_TRACING", "").lower() in ("1", "true", "yes"):
    try:
        from init import init_and_connect

        init_and_connect()
    except Exception as exc:
        logging.getLogger(__name__).warning(
            "AUTO_CONFIGURE_DATABRICKS_TRACING is set but init failed: %s",
            exc,
        )

from observability.adk_defaults import apply_adk_telemetry_defaults
from observability.otel_sdk import configure_otel_from_env

apply_adk_telemetry_defaults()
configure_otel_from_env()

from google.adk.apps import App

try:
    from .workflow import root_agent
except ImportError:
    from workflow import root_agent

app = App(name="SE_workflow_test", root_agent=root_agent)

__all__ = ["root_agent", "app"]
