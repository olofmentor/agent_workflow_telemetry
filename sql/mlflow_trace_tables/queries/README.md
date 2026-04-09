# Example analytics queries

Run these in a Databricks SQL warehouse or notebook against your UC trace schema. Replace `` `dev_ai`.`agent_traces` `` if your catalog/schema differ.

If log or span `attributes` keys differ from your exporter version, inspect one row:  
`SELECT attributes FROM ... LIMIT 1`. Emitter field names are aligned with [`observability/session_logs.py`](../../../observability/session_logs.py) and [`readme-logs.md`](../../../readme-logs.md).

## Core queries

| File | Purpose |
|------|---------|
| [`agent_session_metrics_by_agent.sql`](agent_session_metrics_by_agent.sql) | Sessions, total tokens, and average session wall time **per agent** (from OTLP logs + session bounds). |
| [`trace_steps_inputs_outputs.sql`](trace_steps_inputs_outputs.sql) | Ordered span steps for one `trace_id` with common input/output attribute columns. |
| [`list_trace_ids_for_session.sql`](list_trace_ids_for_session.sql) | Map `session_id` (ADK) to recent `trace_id` values from spans (helper). |

## Additional observability

| File | Purpose |
|------|---------|
| [`per_invocation_llm_tokens.sql`](per_invocation_llm_tokens.sql) | LLM token sums and step counts **per invocation** (`session_id` + `invocation_id` + `agent_name`). |
| [`custom_agent_steps_timeline.sql`](custom_agent_steps_timeline.sql) | Non-LLM log steps (`event_type` ≠ `agent.llm_step`) for workflow / funnel debugging. |
| [`errors_recent_traces_unified.sql`](errors_recent_traces_unified.sql) | Recent **ERROR** root traces from `mlflow_experiment_trace_unified`. |
| [`error_spans.sql`](error_spans.sql) | All spans with non-OK `status.code` (detail beyond root span). |
| [`llm_finish_reason_non_success.sql`](llm_finish_reason_non_success.sql) | LLM log rows with **finish_reason** outside a normal-stop allowlist (tune list for your SDK). |
| [`tool_calls_daily_summary.sql`](tool_calls_daily_summary.sql) | Daily counts of spans carrying ADK **tool_call_args** / **tool_response**. |
| [`span_latency_percentiles_by_name.sql`](span_latency_percentiles_by_name.sql) | **avg / min / max / p50 / p95** span duration by `name` and day (`approx_percentile`). |
| [`trace_ingestion_volume_freshness.sql`](trace_ingestion_volume_freshness.sql) | Daily distinct `trace_id` counts and row volumes (spans vs logs). |
| [`trace_ingestion_max_timestamps.sql`](trace_ingestion_max_timestamps.sql) | Latest span start and log times across tables (ingestion freshness). |
| [`logs_and_spans_timeline_for_trace.sql`](logs_and_spans_timeline_for_trace.sql) | **Union** of logs and spans for one `trace_id`, time-ordered (correlate app logs with spans). |

### Semantics (core)

- **Agent sessions** = distinct `session_id` values where at least one log row carries that `agent_name` (see `observability/session_logs.py`: `agent_name`, `session_id` on OTLP log attributes).
- **Tokens** = sum of `input_tokens`, `output_tokens`, and `reasoning_token_count` on rows with `event_type = 'agent.llm_step'`. Values are stored as strings in `attributes`; the query uses `TRY_CAST`.
- **Average time per session** = average **wall-clock span** of the whole session: `(max - min) time_unix_nano` across all sampled log rows in that session, **in milliseconds**, then averaged over sessions where the agent appears. This includes idle gaps between invocations; adjust the time bounds in SQL if you need per-invocation latency instead.

### `mlflow_experiment_trace_otel_metrics`

Example queries for the metrics table are omitted here; many deployments export spans and logs only. If you emit custom OTEL metrics to the experiment, add tailored aggregations after confirming the table is non-empty.
