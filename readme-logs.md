# Logging: Unity Catalog, MLflow, and session correlation

This project sends **traces (spans)** and **OpenTelemetry logs** to Databricks when `OTEL_EXPORTER_OTLP_ENDPOINT` is set. MLflow links them under the configured experiment (`x-mlflow-experiment-id` header). Unity Catalog tables such as `mlflow_experiment_trace_otel_spans` and `mlflow_experiment_trace_otel_logs` hold the exported data.

## Python `logging` levels used here

| Level | Where | What you see |
|--------|--------|----------------|
| **DEBUG** | Not used by default | Enable with `LOG_LEVEL=DEBUG` to forward DEBUG records to OTLP (if any library emits them). |
| **INFO** | `workflow.py`, `agent.py`, `agents/step_logging.py`, `agents/bootstrap.py`, `agents/reader.py` | Workflow startup, OTEL initialization, each **custom agent step**, and each **LLM step** after the model returns (response text, reasoning text when the model exposes it, token counts). |
| **WARNING** | `agent.py` | Missing optional OpenAI instrumentation package. |
| **ERROR** | — | Standard Python errors if something fails; stack traces are attached to OTLP log attributes when exported. |

Configure minimum severity with:

- `LOG_LEVEL` — default `INFO`. When OTLP is enabled, both the root logger and the OpenTelemetry `LoggingHandler` use this level, so raising it to `WARNING` drops INFO step logs from UC tables.

## OTEL log records emitted by Google ADK (`gcp.vertex.agent`)

These appear in the UC logs table (and MLflow trace UI) and complement spans. Message bodies depend on **`OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT`**:

| Setting | Effect on ADK OTLP **log** bodies |
|---------|-------------------------------------|
| `true` or `1` (default in this repo if unset) | System instruction, user/model messages, and completion choice include real **content**. |
| unset / other | Bodies use **`<elided>`** instead of raw text (spans may still contain payloads; see below). |

**Stable vs experimental GenAI conventions**

- By default ADK uses stable semconv: look for log event names such as `gen_ai.system.message`, `gen_ai.user.message`, and `gen_ai.choice`.
- If you set `OTEL_SEMCONV_STABILITY_OPT_IN=gen_ai_latest_experimental`, ADK expects **`OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT`** to be one of **`EVENT_ONLY`**, **`SPAN_ONLY`**, or **`SPAN_AND_EVENT`** (not `true`) so input/output messages are attached to the `gen_ai.client.inference.operation.details` log. See the [OpenTelemetry GenAI events spec](https://github.com/open-telemetry/semantic-conventions/blob/main/docs/gen-ai/gen-ai-events.md).

This repo sets `OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT=true` by default in `agent.py` only when the variable is **unset**, which suits the **non-experimental** ADK path.

## Span attributes (LLM request/response on spans)

ADK records **`gcp.vertex.agent.llm_request`** and **`gcp.vertex.agent.llm_response`** (JSON) on spans when **`ADK_CAPTURE_MESSAGE_CONTENT_IN_SPANS`** is true (default). Set it to `false` to omit payload text from spans for stricter redaction.

Other useful span attributes include:

- `gen_ai.conversation.id` — same as ADK **session id** (correlates with `session_id` on our INFO logs).
- `gcp.vertex.agent.invocation_id` — one user turn / invocation (also on our INFO logs).
- `gen_ai.usage.experimental.reasoning_tokens` / `reasoning_tokens_limit` — when the model reports “thinking” usage (Gemini-style).

## Application INFO logs (`agents/step_logging.py`)

Every LLM agent registers an `after_model_callback` that logs **`LLM step completed`** with structured `extra` fields exported as OTLP **attributes**, including:

- `event_type`: `agent.llm_step`
- `session_id`, `invocation_id`, `agent_name`, `output_state_key`
- `model_response_text`, `model_reasoning_text` (when the SDK marks thought parts — see Google `Part.thought` / `Part.text`)
- `input_tokens`, `output_tokens`, `reasoning_token_count`, `finish_reason`, character counts

Non-LLM steps log `event_type` values `agent.bootstrap`, `agent.bootstrap_skip`, or `agent.document_reader`.

Truncate oversized text with:

- `AGENT_LOG_RESPONSE_MAX_CHARS` — default `256000`.

## Correlating a full session in Databricks / MLflow

1. Open the trace for a run in MLflow; note **trace id** and span tree (`invoke_agent` → `generate_content …`).
2. In SQL, filter spans on `gen_ai.conversation.id` = `session_id` from logs, or on `gcp.vertex.agent.invocation_id` for a single invocation.
3. Join or filter OTLP **logs** on the same trace context (exported trace/span linkage) and on attributes `session_id` / `invocation_id` from the application logger.

## Privacy note

Enabling message capture (`OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT`, span payloads, and `model_response_text` / `model_reasoning_text` on INFO logs) sends **full prompts and model output** to configured backends. Turn captures off or tighten `AGENT_LOG_RESPONSE_MAX_CHARS` if you ingest sensitive data.
