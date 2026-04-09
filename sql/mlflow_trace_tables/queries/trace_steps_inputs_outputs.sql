-- All spans for one trace, in time order, with common input/output attribute keys.
-- Paste trace_id from MLflow UI, `mlflow_experiment_trace_unified`, or `list_trace_ids_for_session.sql`.

WITH params AS (
  SELECT 'REPLACE_WITH_TRACE_ID' AS trace_id
)

SELECT
  s.trace_id,
  s.span_id,
  s.parent_span_id,
  s.name AS span_name,
  s.kind,
  ROUND(s.start_time_unix_nano / 1000000.0, 3) AS start_time_unix_ms,
  ROUND(s.end_time_unix_nano / 1000000.0, 3) AS end_time_unix_ms,
  ROUND((s.end_time_unix_nano - s.start_time_unix_nano) / 1000000.0, 3) AS duration_ms,
  -- Google ADK / Vertex-style JSON payloads (when ADK_CAPTURE_MESSAGE_CONTENT_IN_SPANS=true)
  s.attributes['gcp.vertex.agent.llm_request'] AS llm_request_json,
  s.attributes['gcp.vertex.agent.llm_response'] AS llm_response_json,
  s.attributes['gcp.vertex.agent.tool_call_args'] AS tool_call_args_json,
  s.attributes['gcp.vertex.agent.tool_response'] AS tool_response_json,
  -- OpenTelemetry GenAI conventions (stable / experimental depending on SDK)
  s.attributes['gen_ai.input.messages'] AS gen_ai_input_messages,
  s.attributes['gen_ai.output.messages'] AS gen_ai_output_messages,
  -- MLflow / other mirrors (unified view uses these in COALESCE)
  s.attributes['mlflow.spanInputs'] AS mlflow_span_inputs,
  s.attributes['mlflow.spanOutputs'] AS mlflow_span_outputs,
  s.attributes['traceloop.entity.input'] AS traceloop_input,
  s.attributes['traceloop.entity.output'] AS traceloop_output,
  s.attributes['input.value'] AS input_value_attr,
  s.attributes['output.value'] AS output_value_attr,
  -- Usage (often on LLM spans; keys vary by instrumentation version)
  s.attributes['gen_ai.usage.input_tokens'] AS gen_ai_input_tokens,
  s.attributes['gen_ai.usage.output_tokens'] AS gen_ai_output_tokens,
  s.attributes['gen_ai.usage.experimental.reasoning_tokens'] AS gen_ai_reasoning_tokens,
  s.status.message AS status_message,
  s.status.code AS status_code,
  -- Full map for ad-hoc inspection (can be large)
  s.attributes AS all_attributes
FROM `dev_ai`.`agent_traces`.`mlflow_experiment_trace_otel_spans` s
CROSS JOIN params p
WHERE s.trace_id = p.trace_id
ORDER BY s.start_time_unix_nano ASC;
