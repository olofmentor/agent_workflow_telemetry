# Logging: Unity Catalog, MLflow, and session correlation

This project sends **traces (spans)** and **OpenTelemetry logs** to Databricks when `OTEL_EXPORTER_OTLP_ENDPOINT` is set. MLflow links them under the configured experiment (`x-mlflow-experiment-id` header). Unity Catalog tables such as `mlflow_experiment_trace_otel_spans` and `mlflow_experiment_trace_otel_logs` hold the exported data. **Without** an endpoint, nothing is exported to those tables: `configure_otel_from_env` installs a no-op tracer and does not attach the OTLP `LoggingHandler` to the root logger.

## Python `logging` levels used here

| Level | Where | What you see |
|--------|--------|----------------|
| **DEBUG** | `observability/otel_sdk.py` (and any library at DEBUG) | With `LOG_LEVEL=DEBUG`, duplicate `configure_otel_from_env` calls log skip messages; other libraries may emit DEBUG as well. |
| **INFO** | `workflow.py`, `observability/otel_sdk.py`, `observability/session_logs.py` | Workflow startup, OTEL initialization, each **custom agent step** and **LLM step** (custom/LLM calls originate from `agents/*` and `adk_templates.instrumented_llm_agent`, but records use the `observability.session_logs` / OTEL loggers). LLM INFO includes response text, reasoning when the model exposes it, and token counts. |
| **WARNING** | `agent.py` | Failed Databricks init when `AUTO_CONFIGURE_DATABRICKS_TRACING` is set (see log message). |
| **WARNING** | `observability/otel_sdk.py` | Optional OpenAI instrumentation package not installed. |
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

This repo sets `OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT=true` by default in `observability/adk_defaults.py` (`apply_adk_telemetry_defaults()`), which `agent.py` calls at import, only when the variable is **absent** from the environment—this suits the **non-experimental** ADK path.

## Span attributes (LLM request/response on spans)

ADK records **`gcp.vertex.agent.llm_request`** and **`gcp.vertex.agent.llm_response`** (JSON) on spans when **`ADK_CAPTURE_MESSAGE_CONTENT_IN_SPANS`** is true (default). Set it to `false` to omit payload text from spans for stricter redaction.

Other useful span attributes include:

- `gen_ai.conversation.id` — same as ADK **session id** (correlates with `session_id` on our INFO logs).
- `gcp.vertex.agent.invocation_id` — one user turn / invocation (also on our INFO logs).
- `gen_ai.usage.experimental.reasoning_tokens` / `reasoning_tokens_limit` — when the model reports “thinking” usage (Gemini-style).

## Application INFO logs (`observability/session_logs.py` + `adk_templates/instrumented_llm.py`)

LLM agents should be built with **`instrumented_llm_agent`** (from **`adk_templates`**; factory implemented in **`observability.llm_callbacks`**), which registers an `after_model_callback` that logs **`LLM step completed`** with structured `extra` fields exported as OTLP **attributes**, including:

- `event_type`: `agent.llm_step`
- `session_id`, `invocation_id`, `agent_name`, `output_state_key`
- `model_response_text`, `model_reasoning_text` (when the SDK marks thought parts — see Google `Part.thought` / `Part.text`)
- `input_tokens`, `output_tokens`, `reasoning_token_count`, `finish_reason`, character counts

Non-LLM steps log `event_type` values `agent.bootstrap`, `agent.bootstrap_skip`, or `agent.document_reader`.

Truncate oversized text with:

- `AGENT_LOG_RESPONSE_MAX_CHARS` — default `256000`.

### Optional fields on `log_agent_step` (non-LLM agents)

`log_agent_step` accepts **`**extra_fields`** after `message`. Each keyword becomes a **log attribute** alongside the built-in keys (`event_type`, `session_id`, `invocation_id`, `agent_name`). Values must be **OTLP-safe scalars** so the stdlib `logging` `extra` payload can be exported cleanly: **`str`**, **`int`**, **`float`**, **`bool`**, or **`None`** (see `OtlpExtraValue` in `observability/session_logs.py`). Do **not** pass lists, dicts, or arbitrary objects—those may break or be dropped by the exporter.

**How to add information**

1. **Pick stable attribute names** (snake_case), e.g. `files_indexed`, `preview_used`, `duration_ms`.
2. **Pass them as keyword arguments** after the human-readable `message`:

```python
log_agent_step(
    "document_reader",
    ctx,
    "Indexed project docs",
    files_indexed=12,
    previews_only=True,
    notes="optional string detail",
)
```

3. **Structured or nested data** — encode as a **single string** (e.g. JSON) if you need more than one field’s worth of detail: `manifest_summary='{"ok":9,"skipped":3}'`. Prefer short strings so UC log attributes stay readable.
4. **Querying** — in Databricks SQL or MLflow log views, filter or project the same attribute names you passed.

LLM turns use `log_llm_step_completed` with a fixed schema; to add fields there, extend `observability/session_logs.py` in that function (and keep values scalar-friendly) rather than overloading `log_agent_step`.

## Correlating a full session in Databricks / MLflow

1. Open the trace for a run in MLflow; note **trace id** and span tree (`invoke_agent` → `generate_content …`).
2. In SQL, filter spans on `gen_ai.conversation.id` = `session_id` from logs, or on `gcp.vertex.agent.invocation_id` for a single invocation.
3. Join or filter OTLP **logs** on the same trace context (exported trace/span linkage) and on attributes `session_id` / `invocation_id` from the application logger.

## Privacy note

Enabling message capture (`OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT`, span payloads, and `model_response_text` / `model_reasoning_text` on INFO logs) sends **full prompts and model output** to configured backends. Turn captures off or tighten `AGENT_LOG_RESPONSE_MAX_CHARS` if you ingest sensitive data.
