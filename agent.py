import os
import logging
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from opentelemetry import trace, _logs
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.otlp.proto.http._log_exporter import OTLPLogExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
import atexit

# Get OTEL configuration from environment
endpoint = os.getenv('OTEL_EXPORTER_OTLP_ENDPOINT')
headers_str = os.getenv('OTEL_EXPORTER_OTLP_HEADERS', '')
service_name = os.getenv('OTEL_SERVICE_NAME', 'SE_workflow_test')

if endpoint:
    # Parse headers from environment
    headers = {}
    if headers_str:
        for part in headers_str.split(','):
            if '=' in part:
                key, value = part.split('=', 1)
                headers[key.strip()] = value.strip()
    
    # Create shared resource
    resource = Resource.create({"service.name": service_name})
    
    # Setup tracer provider with configuration
    tracer_provider = TracerProvider(resource=resource)
    exporter = OTLPSpanExporter(endpoint=endpoint, headers=headers)
    tracer_provider.add_span_processor(BatchSpanProcessor(exporter))
    trace.set_tracer_provider(tracer_provider)
    
    # Setup logger provider with configuration
    # Use logs endpoint instead of traces
    logs_endpoint = endpoint.replace('/traces', '/logs')
    
    # Create separate headers for logs with the correct table name
    logs_headers = headers.copy()
    if 'X-Databricks-UC-Table-Name' in logs_headers:
        # Replace the spans table with the logs table
        logs_headers['X-Databricks-UC-Table-Name'] = logs_headers['X-Databricks-UC-Table-Name'].replace(
            'mlflow_experiment_trace_otel_spans',
            'mlflow_experiment_trace_otel_logs'
        )
    
    log_exporter = OTLPLogExporter(endpoint=logs_endpoint, headers=logs_headers)
    logger_provider = LoggerProvider(resource=resource)
    logger_provider.add_log_record_processor(BatchLogRecordProcessor(log_exporter))
    
    # Set the global logger provider
    _logs.set_logger_provider(logger_provider)
    
    # Attach OTEL handler to root logger
    handler = LoggingHandler(level=logging.INFO, logger_provider=logger_provider)
    logging.getLogger().addHandler(handler)
    logging.getLogger().setLevel(logging.INFO)
    
    # Register shutdown handlers to ensure logs are flushed
    def shutdown_telemetry():
        logger_provider.force_flush(timeout_millis=5000)
        logger_provider.shutdown()
        tracer_provider.force_flush(timeout_millis=5000)
        tracer_provider.shutdown()
    
    atexit.register(shutdown_telemetry)
    
    # Enable OpenAI instrumentation for LiteLLM/OpenAI calls
    try:
        from opentelemetry.instrumentation.openai_v2 import OpenAIInstrumentor
        OpenAIInstrumentor().instrument()
        print(f"✓ OpenAI instrumentation enabled")
        logging.info("OpenAI instrumentation enabled successfully")
    except ImportError:
        print(f"⚠️  opentelemetry-instrumentation-openai-v2 not installed")
        logging.warning("opentelemetry-instrumentation-openai-v2 not installed")
    
    print(f"✓ OpenTelemetry tracing enabled: {service_name} -> {endpoint}")
    print(f"✓ OpenTelemetry logging enabled: {service_name} -> {logs_endpoint}")
    logging.info(f"OpenTelemetry initialized: service={service_name}, traces={endpoint}, logs={logs_endpoint}")
else:
    # Fallback to basic setup without OTLP export
    tracer_provider = TracerProvider()
    trace.set_tracer_provider(tracer_provider)
    print("⚠️  OpenTelemetry tracing enabled but no OTLP endpoint configured")



from google.adk.apps import App

from .workflow import root_agent

app = App(name="SE_workflow_test", root_agent=root_agent)

__all__ = ["root_agent", "app"]
