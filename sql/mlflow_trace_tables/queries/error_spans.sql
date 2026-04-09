-- Spans whose OTEL status is not OK (detailed; includes non-root spans).
-- OK semantics match mlflow_experiment_trace_unified root_span: NULL or STATUS_CODE_OK.

SELECT
  s.trace_id,
  s.span_id,
  s.parent_span_id,
  s.name AS span_name,
  ROUND(s.start_time_unix_nano / 1000000.0, 3) AS start_time_unix_ms,
  ROUND(s.end_time_unix_nano / 1000000.0, 3) AS end_time_unix_ms,
  ROUND((s.end_time_unix_nano - s.start_time_unix_nano) / 1000000.0, 3) AS duration_ms,
  s.status.code AS status_code,
  s.status.message AS status_message,
  s.attributes['gen_ai.conversation.id'] AS gen_ai_conversation_id,
  s.attributes['gcp.vertex.agent.invocation_id'] AS vertex_invocation_id
FROM `dev_ai`.`agent_traces`.`mlflow_experiment_trace_otel_spans` s
WHERE NOT (
  s.status.code IS NULL
  OR s.status.code = 'STATUS_CODE_OK'
)

-- Optional time filter:
-- AND s.end_time_unix_nano >= CAST(UNIX_TIMESTAMP(TIMESTAMP '2026-02-01 00:00:00') AS BIGINT) * 1000000000

ORDER BY s.end_time_unix_nano DESC
LIMIT 2000;
