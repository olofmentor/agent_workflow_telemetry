-- Spans that carry ADK tool call/response JSON (see trace_steps_inputs_outputs.sql).
-- Daily counts for tool-heavy vs LLM-only traces.

WITH tool_spans AS (
  SELECT
    trace_id,
    name AS span_name,
    DATE_TRUNC('DAY', TIMESTAMP_MILLIS(CAST(start_time_unix_nano / 1000000 AS BIGINT))) AS day,
    attributes['gen_ai.conversation.id'] AS conversation_id,
    COALESCE(attributes['gcp.vertex.agent.tool_call_args'], '') AS tool_args,
    COALESCE(attributes['gcp.vertex.agent.tool_response'], '') AS tool_resp
  FROM `dev_ai`.`agent_traces`.`mlflow_experiment_trace_otel_spans`
  WHERE (
    (attributes['gcp.vertex.agent.tool_call_args'] IS NOT NULL AND TRIM(attributes['gcp.vertex.agent.tool_call_args']) != '')
    OR (attributes['gcp.vertex.agent.tool_response'] IS NOT NULL AND TRIM(attributes['gcp.vertex.agent.tool_response']) != '')
  )
)

SELECT
  day,
  span_name,
  COUNT(*) AS tool_span_count,
  COUNT(DISTINCT trace_id) AS distinct_traces,
  COUNT(DISTINCT conversation_id) AS distinct_conversation_ids
FROM tool_spans
GROUP BY day, span_name
ORDER BY day DESC, tool_span_count DESC;
