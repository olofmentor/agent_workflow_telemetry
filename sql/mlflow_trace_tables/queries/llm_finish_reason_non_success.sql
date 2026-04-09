-- LLM log rows where finish_reason is present and not a normal stop.
-- Values come from str(LlmResponse.finish_reason) in observability/session_logs.py; extend the allowlist if your SDK differs.

SELECT
  TIMESTAMP_MILLIS(CAST(time_unix_nano / 1000000 AS BIGINT)) AS log_time,
  trace_id,
  attributes['session_id'] AS session_id,
  attributes['invocation_id'] AS invocation_id,
  attributes['agent_name'] AS agent_name,
  attributes['finish_reason'] AS finish_reason,
  attributes['output_state_key'] AS output_state_key,
  body
FROM `dev_ai`.`agent_traces`.`mlflow_experiment_trace_otel_logs`
WHERE attributes['event_type'] = 'agent.llm_step'
  AND attributes['finish_reason'] IS NOT NULL
  AND TRIM(attributes['finish_reason']) != ''
  AND UPPER(TRIM(attributes['finish_reason'])) NOT IN (
    'STOP',
    'FINISH_REASON_STOP',
    'END_TURN',
    'FINISH_REASON_END_TURN'
  )

ORDER BY time_unix_nano DESC
LIMIT 500;
