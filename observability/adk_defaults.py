"""Centralize environment defaults consumed by Google ADK Open Telemetry instrumentation."""

from __future__ import annotations

import os


def apply_adk_telemetry_defaults() -> None:
    """Set ADK-related OTEL env defaults when unset (mutates ``os.environ``).

    Without ``OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT``, ADK emits
    ``<elided>`` for OTLP log bodies (gen_ai.user.message, gen_ai.choice, etc.).
    """
    if "OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT" not in os.environ:
        os.environ["OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT"] = "true"
