"""Configure OpenTelemetry SDK (traces + logs) from environment for Databricks OTLP."""

from __future__ import annotations

import atexit
import logging
import os

from opentelemetry import _logs, trace
from opentelemetry.exporter.otlp.proto.http._log_exporter import OTLPLogExporter
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from observability.otlp_headers import parse_otel_headers

_export_otel_configured: bool = False
_noop_otel_configured: bool = False


def otlp_export_initialized() -> bool:
    """True after a successful OTLP exporter setup (for tests / diagnostics)."""
    return _export_otel_configured


def _logs_headers_for_databricks(headers: dict[str, str]) -> dict[str, str]:
    logs_headers = headers.copy()
    if "X-Databricks-UC-Table-Name" in logs_headers:
        logs_headers["X-Databricks-UC-Table-Name"] = logs_headers[
            "X-Databricks-UC-Table-Name"
        ].replace(
            "mlflow_experiment_trace_otel_spans",
            "mlflow_experiment_trace_otel_logs",
        )
    return logs_headers


def configure_otel_from_env(
    *,
    log: logging.Logger | None = None,
    use_print_status: bool = True,
) -> bool:
    """
    Configure global tracer and logger providers from ``os.environ``.

    Returns True if an OTLP endpoint was configured and exporters were installed.
    Safe to call more than once: subsequent calls are no-ops (see module-level guards).

    If the first call had no endpoint (noop tracer only) and ``OTEL_EXPORTER_OTLP_ENDPOINT``
    is set later, the next call performs full OTLP setup. Prefer setting env before import.
    """
    global _export_otel_configured, _noop_otel_configured

    log = log or logging.getLogger(__name__)

    endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "").strip()
    headers_str = os.getenv("OTEL_EXPORTER_OTLP_HEADERS", "")
    service_name = os.getenv("OTEL_SERVICE_NAME", "SE_workflow_test")
    log_level = getattr(
        logging,
        os.getenv("LOG_LEVEL", "INFO").upper(),
        logging.INFO,
    )

    if _export_otel_configured:
        log.debug("configure_otel_from_env: OTLP export already initialized; skipping")
        return True

    if not endpoint:
        if _noop_otel_configured:
            log.debug("configure_otel_from_env: noop tracer already initialized; skipping")
            return False
        tracer_provider = TracerProvider()
        trace.set_tracer_provider(tracer_provider)
        _noop_otel_configured = True
        if use_print_status:
            print("⚠️  OpenTelemetry tracing enabled but no OTLP endpoint configured")
        return False

    headers = parse_otel_headers(headers_str)
    resource = Resource.create({"service.name": service_name})

    tracer_provider = TracerProvider(resource=resource)
    tracer_provider.add_span_processor(
        BatchSpanProcessor(OTLPSpanExporter(endpoint=endpoint, headers=headers))
    )
    trace.set_tracer_provider(tracer_provider)

    logs_endpoint = endpoint.replace("/traces", "/logs")
    log_exporter = OTLPLogExporter(
        endpoint=logs_endpoint,
        headers=_logs_headers_for_databricks(headers),
    )
    logger_provider = LoggerProvider(resource=resource)
    logger_provider.add_log_record_processor(BatchLogRecordProcessor(log_exporter))
    _logs.set_logger_provider(logger_provider)

    handler = LoggingHandler(level=log_level, logger_provider=logger_provider)
    root = logging.getLogger()
    root.addHandler(handler)
    root.setLevel(log_level)

    def shutdown_telemetry():
        logger_provider.force_flush(timeout_millis=5000)
        logger_provider.shutdown()
        tracer_provider.force_flush(timeout_millis=5000)
        tracer_provider.shutdown()

    atexit.register(shutdown_telemetry)

    try:
        from opentelemetry.instrumentation.openai_v2 import OpenAIInstrumentor

        OpenAIInstrumentor().instrument()
        if use_print_status:
            print("✓ OpenAI instrumentation enabled")
        log.info("OpenAI instrumentation enabled successfully")
    except ImportError:
        if use_print_status:
            print("⚠️  opentelemetry-instrumentation-openai-v2 not installed")
        log.warning("opentelemetry-instrumentation-openai-v2 not installed")

    if use_print_status:
        print(f"✓ OpenTelemetry tracing enabled: {service_name} -> {endpoint}")
        print(f"✓ OpenTelemetry logging enabled: {service_name} -> {logs_endpoint}")
    log.info(
        "OpenTelemetry initialized: service=%s, traces=%s, logs=%s",
        service_name,
        endpoint,
        logs_endpoint,
    )
    _export_otel_configured = True
    return True
