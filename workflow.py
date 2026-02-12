import os
from google.adk.agents import SequentialAgent
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.resources import Resource

from .agents.bootstrap import UserQuestionBootstrapAgent
from .agents.clarifier import build_clarifier_agent
from .agents.reader import DocumentReaderAgent
from .agents.summarizer import build_summarizer_agent
from .agents.synthesizer import build_synthesizer_agent
from .config import load_config


def setup_tracing():
    """
    Initialize OpenTelemetry tracer provider for MLflow integration.
    
    This follows the official MLflow + Google ADK integration pattern:
    https://mlflow.org/docs/latest/genai/tracing/integrations/listing/google-adk/
    
    The tracer provider must be set up BEFORE creating agents so that
    Google ADK can automatically generate traces.
    """
    # Get config from environment
    endpoint = os.getenv('OTEL_EXPORTER_OTLP_ENDPOINT')
    headers_str = os.getenv('OTEL_EXPORTER_OTLP_HEADERS', '')
    service_name = os.getenv('OTEL_SERVICE_NAME', 'agent_workflow')
    
    if not endpoint:
        print("⚠️  Warning: OTEL_EXPORTER_OTLP_ENDPOINT not set. Tracing disabled.")
        return
    
    # Parse headers from comma-separated key=value pairs
    headers = {}
    if headers_str:
        for part in headers_str.split(','):
            if '=' in part:
                key, value = part.split('=', 1)
                headers[key.strip()] = value.strip()
    
    try:
        # Create tracer provider with service resource
        resource = Resource.create({"service.name": service_name})
        provider = TracerProvider(resource=resource)
        
        # Create OTLP exporter with endpoint and headers
        exporter = OTLPSpanExporter(endpoint=endpoint, headers=headers)
        
        # Use BatchSpanProcessor for better performance
        processor = BatchSpanProcessor(exporter)
        provider.add_span_processor(processor)
        
        # Set as global tracer provider
        trace.set_tracer_provider(provider)
        
        print(f"✓ OpenTelemetry tracing enabled")
        print(f"  Service: {service_name}")
        print(f"  Endpoint: {endpoint}")
        
    except Exception as e:
        print(f"⚠️  Failed to initialize tracing: {e}")
        print("   Workflow will run without tracing.")


def build_workflow() -> SequentialAgent:
    # Initialize OpenTelemetry tracing FIRST, before creating any agents
    # This allows Google ADK to automatically generate traces
    setup_tracing()
    
    config = load_config()

    agent0_bootstrap = UserQuestionBootstrapAgent(
        documents_dir=config.documents_dir
    )
    agent1_clarify = build_clarifier_agent(config.model_name)
    agent2_reader = DocumentReaderAgent(
        documents_dir=config.documents_dir,
        max_file_chars=config.max_file_chars,
        preview_chars=config.preview_chars,
        prefer_previews=config.prefer_previews,
    )
    agent1_summarize = build_summarizer_agent(config.model_name)
    agent3_synthesize = build_synthesizer_agent(config.model_name)

    return SequentialAgent(
        name="LessonsLearnedWorkflow",
        sub_agents=[
            agent0_bootstrap,
            agent1_clarify,
            agent2_reader,
            agent1_summarize,
            agent3_synthesize,
        ],
    )


root_agent = build_workflow()
