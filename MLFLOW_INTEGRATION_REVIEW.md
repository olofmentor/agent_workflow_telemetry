# MLflow + Google ADK Integration Review

## Overview
This document compares the current implementation against the official MLflow documentation for Google ADK tracing integration.

**Documentation Source**: https://mlflow.org/docs/latest/genai/tracing/integrations/listing/google-adk/

---

## ✅ What's Working Correctly

### 1. OpenTelemetry Installation
**MLflow Docs Requirement:**
```bash
pip install 'mlflow[genai]>=3.6.0' google-adk opentelemetry-exporter-otlp-proto-http
```

**Current Implementation:**
- ✅ `google-adk` installed (requirements.txt)
- ✅ `opentelemetry-exporter-otlp-proto-http` installed manually
- ❓ `mlflow[genai]>=3.6.0` - **NOT in requirements.txt**

### 2. OpenTelemetry Configuration
**MLflow Docs Requirement:**
```bash
export OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:5000
export OTEL_EXPORTER_OTLP_HEADERS=x-mlflow-experiment-id=123
```

**Current Implementation (.env):**
```env
OTEL_EXPORTER_OTLP_ENDPOINT="https://adb-957977613266276.16.azuredatabricks.net/api/2.0/otel/v1/traces"
OTEL_EXPORTER_OTLP_HEADERS="Authorization=Bearer dapi9...,x-mlflow-experiment-id=3078644569850998,X-Databricks-UC-Table-Name=main.agent_traces.otel_traces"
```

✅ **Correctly configured** for Databricks (instead of local MLflow server)

### 3. Tracer Provider Setup
**MLflow Docs Requirement:**
```python
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor

# Configure the tracer provider and add the exporter
tracer_provider = TracerProvider()
tracer_provider.add_span_processor(
    SimpleSpanProcessor(OTLPSpanExporter())
)
trace.set_tracer_provider(tracer_provider)
```

**Current Implementation (`telemetry/core.py`):**
```python
# Similar setup in DatabricksOtelSink class
resource = Resource.create({"service.name": app_name})
provider = TracerProvider(resource=resource)
exporter = OTLPSpanExporter(endpoint=endpoint, headers=headers)
provider.add_span_processor(BatchSpanProcessor(exporter))  # BatchSpanProcessor instead of SimpleSpanProcessor
trace.set_tracer_provider(provider)
```

✅ **Implementation is correct** (BatchSpanProcessor is better for production than SimpleSpanProcessor)

---

## ❌ Critical Issues

### Issue #1: TracerProvider Setup Not Called Before Agent Runs

**MLflow Docs Requirement:**
> "To enable tracing for Google ADK and send traces to MLflow, **set up the OpenTelemetry tracer provider** with the OTLPSpanExporter **BEFORE running the agent**."

**Current Problem:**
The `workflow.py` file creates agents but **never calls** the tracer setup:

```python
# workflow.py - NO tracer setup!
from google.adk.agents import SequentialAgent
from .agents.bootstrap import UserQuestionBootstrapAgent
# ... other imports

def build_workflow() -> SequentialAgent:
    config = load_config()
    # ... build agents
    return SequentialAgent(name="LessonsLearnedWorkflow", sub_agents=[...])

root_agent = build_workflow()
```

**The telemetry setup code exists** (`telemetry/core.py`) **but is never imported or executed** in the workflow entry point!

### Issue #2: Legacy Telemetry Plugin Approach

The repository has a custom `telemetry/` module with `DatabricksOtelSink` that seems to be from an older approach. According to MLflow docs, **Google ADK automatically generates traces** when the tracer provider is configured - you don't need a custom sink.

**Old Approach (current):**
```python
# Custom sink that manually creates spans
class DatabricksOtelSink(TelemetrySink):
    def record(self, event: TelemetryEvent) -> None:
        with self.tracer.start_as_current_span(event.name) as span:
            for key, value in event.attributes.items():
                span.set_attribute(key, _coerce_str(value))
```

**MLflow Recommended Approach:**
```python
# Just set up the tracer provider ONCE before running agents
# Google ADK will automatically create traces
tracer_provider = TracerProvider()
tracer_provider.add_span_processor(SimpleSpanProcessor(OTLPSpanExporter()))
trace.set_tracer_provider(tracer_provider)

# Then run agents normally - traces are automatic!
root_agent = LlmAgent(...)
```

### Issue #3: Missing mlflow[genai] Package

**MLflow Docs:** Requires `mlflow[genai]>=3.6.0`

**Current requirements.txt:**
```
google-adk
litellm>=1.75.5
pypdf
```

Missing the MLflow package entirely! This might be why traces aren't working properly.

---

## 🔧 Recommended Fixes

### Fix #1: Add MLflow to Requirements

**requirements.txt:**
```diff
 google-adk
 litellm>=1.75.5
 pypdf
+mlflow[genai]>=3.6.0
+opentelemetry-exporter-otlp-proto-http
```

### Fix #2: Initialize Tracer Provider in workflow.py

**workflow.py (BEFORE agent creation):**
```python
from google.adk.agents import SequentialAgent
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.resources import Resource
import os

from .agents.bootstrap import UserQuestionBootstrapAgent
from .agents.clarifier import build_clarifier_agent
from .agents.reader import DocumentReaderAgent
from .agents.summarizer import build_summarizer_agent
from .agents.synthesizer import build_synthesizer_agent
from .config import load_config


def setup_tracing():
    """Initialize OpenTelemetry tracer provider for MLflow."""
    # Get config from environment
    endpoint = os.getenv('OTEL_EXPORTER_OTLP_ENDPOINT')
    headers_str = os.getenv('OTEL_EXPORTER_OTLP_HEADERS', '')
    service_name = os.getenv('OTEL_SERVICE_NAME', 'agent_workflow')
    
    if not endpoint:
        print("Warning: OTEL_EXPORTER_OTLP_ENDPOINT not set. Tracing disabled.")
        return
    
    # Parse headers
    headers = {}
    if headers_str:
        for part in headers_str.split(','):
            if '=' in part:
                key, value = part.split('=', 1)
                headers[key.strip()] = value.strip()
    
    # Create tracer provider
    resource = Resource.create({"service.name": service_name})
    provider = TracerProvider(resource=resource)
    exporter = OTLPSpanExporter(endpoint=endpoint, headers=headers)
    processor = BatchSpanProcessor(exporter)
    provider.add_span_processor(processor)
    trace.set_tracer_provider(provider)
    
    print(f"✓ Tracing enabled: {service_name} -> {endpoint}")


def build_workflow() -> SequentialAgent:
    # Initialize tracing FIRST
    setup_tracing()
    
    config = load_config()

    agent0_bootstrap = UserQuestionBootstrapAgent(
        documents_dir=config.documents_dir
    )
    # ... rest of agent creation
    
    return SequentialAgent(
        name="LessonsLearnedWorkflow",
        sub_agents=[...],
    )


root_agent = build_workflow()
```

### Fix #3: Remove Workaround Scripts

Once the tracer provider is properly initialized in `workflow.py`, you **don't need**:
- ❌ `run_with_traces.sh` with `opentelemetry-instrument` wrapper
- ❌ Custom `telemetry/` module (unless you want additional custom telemetry)

The traces will be **automatically generated** by Google ADK when the tracer provider is set.

### Fix #4: Simplified Execution

**Just run the agent normally:**
```bash
adk run agent_workflow_telemetry
```

Or programmatically:
```python
result = await root_agent.run(session_state={"user_question": question})
```

Traces will automatically flow to Databricks MLflow!

---

## 🎯 Key Differences: Current vs. MLflow Approach

| Aspect | Current Implementation | MLflow Recommended |
|--------|----------------------|-------------------|
| **Tracer Setup** | In separate `telemetry/core.py`, never called | In `workflow.py` before agent creation |
| **Trace Generation** | Manual via custom `TelemetrySink` | Automatic via Google ADK |
| **Execution** | Using `opentelemetry-instrument` wrapper | Direct `adk run` command |
| **Dependencies** | Missing `mlflow[genai]` | Requires `mlflow[genai]>=3.6.0` |
| **Span Processor** | BatchSpanProcessor (✓ correct) | SimpleSpanProcessor (docs example) |

---

## 📋 Implementation Checklist

To align with MLflow docs:

- [ ] Add `mlflow[genai]>=3.6.0` to requirements.txt
- [ ] Add `opentelemetry-exporter-otlp-proto-http` to requirements.txt
- [ ] Add `setup_tracing()` function to workflow.py
- [ ] Call `setup_tracing()` in `build_workflow()` BEFORE creating agents
- [ ] Test with direct `adk run` command (not wrapper script)
- [ ] Optional: Keep `telemetry/` module for custom telemetry events
- [ ] Verify traces appear in Databricks after UC table permissions are granted

---

## 💡 Why Traces Aren't Appearing

**Root Cause**: The tracer provider is never initialized before Google ADK runs!

1. `workflow.py` creates agents but doesn't set up tracing
2. `telemetry/core.py` has the setup code but it's never imported/called
3. `run_with_traces.sh` tries to use `opentelemetry-instrument` auto-instrumentation, but:
   - Google ADK needs **explicit** tracer provider setup (not just auto-instrumentation)
   - Auto-instrumentation works for HTTP/gRPC but ADK needs the tracer provider

**Solution**: Add the tracer provider setup **directly in workflow.py** before creating agents, exactly as shown in MLflow docs.

---

## 🚀 Next Steps

1. **Update requirements.txt** with mlflow[genai]
2. **Modify workflow.py** to initialize tracer provider
3. **Install new dependencies**: `pip install -r requirements.txt`
4. **Create UC table** in Databricks (using the DDL scripts)
5. **Run workflow directly**: `adk run agent_workflow_telemetry`
6. **Check traces** in MLflow UI after 1-2 minutes

Once the tracer provider is initialized in the right place, traces should flow automatically! 🎉
