"""Tests for observability/otel_sdk and adk_defaults."""

import logging
import os
import subprocess
import sys
import textwrap
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from observability.adk_defaults import apply_adk_telemetry_defaults
from observability.otel_sdk import configure_otel_from_env


def test_apply_adk_telemetry_defaults_sets_capture_when_missing(monkeypatch):
    monkeypatch.delenv("OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT", raising=False)
    apply_adk_telemetry_defaults()
    assert os.environ.get("OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT") == "true"


def test_apply_adk_telemetry_defaults_respects_existing(monkeypatch):
    monkeypatch.setenv("OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT", "false")
    apply_adk_telemetry_defaults()
    assert os.environ.get("OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT") == "false"


def test_configure_otel_returns_false_without_endpoint(monkeypatch):
    monkeypatch.delenv("OTEL_EXPORTER_OTLP_ENDPOINT", raising=False)
    log = logging.getLogger("test_otel_sdk")
    assert configure_otel_from_env(log=log, use_print_status=False) is False


def test_configure_otel_from_env_is_idempotent_for_noop_path():
    """Second call with no OTLP endpoint must not duplicate setup (subprocess-isolated)."""
    root = Path(__file__).resolve().parent.parent
    code = textwrap.dedent(
        f"""
        import logging
        import os
        import sys
        sys.path.insert(0, {str(root)!r})
        os.environ.pop("OTEL_EXPORTER_OTLP_ENDPOINT", None)
        from observability.otel_sdk import configure_otel_from_env
        log = logging.getLogger("sub_otel")
        assert configure_otel_from_env(log=log, use_print_status=False) is False
        assert configure_otel_from_env(log=log, use_print_status=False) is False
        """
    ).strip()
    subprocess.run([sys.executable, "-c", code], check=True, cwd=str(root))
