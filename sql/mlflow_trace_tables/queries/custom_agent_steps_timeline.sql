-- Non-LLM agent steps from OTLP logs (bootstrap, document_reader, etc.).
-- Excludes agent.llm_step; same attribute schema as observability/session_logs.py.

SELECT
  TIMESTAMP_MILLIS(CAST(time_unix_nano / 1000000 AS BIGINT)) AS log_time,
  time_unix_nano,
  trace_id,
  attributes['session_id'] AS session_id,
  attributes['invocation_id'] AS invocation_id,
  attributes['agent_name'] AS agent_name,
  attributes['event_type'] AS event_type,
  severity_text,
  body,
  attributes
FROM `dev_ai`.`agent_traces`.`mlflow_experiment_trace_otel_logs`
WHERE attributes['event_type'] IS NOT NULL
  AND TRIM(attributes['event_type']) != ''
  AND attributes['event_type'] != 'agent.llm_step'
  AND attributes['session_id'] IS NOT NULL
  AND TRIM(attributes['session_id']) != ''

-- Optional: filter one session
-- AND attributes['session_id'] = 'REPLACE_WITH_SESSION_ID'

ORDER BY time_unix_nano ASC;
