-- LLM token and step counts per ADK invocation (session + invocation_id).
-- See observability/session_logs.py: agent.llm_step rows carry session_id, invocation_id, agent_name.
-- Replace catalog/schema if needed.

WITH log_rows AS (
  SELECT
    attributes['session_id'] AS session_id,
    attributes['invocation_id'] AS invocation_id,
    attributes['agent_name'] AS agent_name,
    TRY_CAST(NULLIF(TRIM(attributes['input_tokens']), '') AS BIGINT) AS input_tokens,
    TRY_CAST(NULLIF(TRIM(attributes['output_tokens']), '') AS BIGINT) AS output_tokens,
    TRY_CAST(NULLIF(TRIM(attributes['reasoning_token_count']), '') AS BIGINT) AS reasoning_tokens,
    time_unix_nano,
    trace_id
  FROM `dev_ai`.`agent_traces`.`mlflow_experiment_trace_otel_logs`
  WHERE attributes['event_type'] = 'agent.llm_step'
    AND attributes['session_id'] IS NOT NULL
    AND TRIM(attributes['session_id']) != ''
    -- Optional: AND time_unix_nano >= CAST(UNIX_TIMESTAMP(TIMESTAMP '2026-02-01 00:00:00') AS BIGINT) * 1000000000
),

per_invocation AS (
  SELECT
    session_id,
    invocation_id,
    agent_name,
    COUNT(*) AS llm_step_count,
    SUM(COALESCE(input_tokens, 0)) AS sum_input_tokens,
    SUM(COALESCE(output_tokens, 0)) AS sum_output_tokens,
    SUM(COALESCE(reasoning_tokens, 0)) AS sum_reasoning_tokens,
    MIN(time_unix_nano) AS first_log_nano,
    MAX(time_unix_nano) AS last_log_nano,
    MAX(trace_id) AS sample_trace_id
  FROM log_rows
  GROUP BY session_id, invocation_id, agent_name
)

SELECT
  session_id,
  invocation_id,
  agent_name,
  llm_step_count,
  sum_input_tokens,
  sum_output_tokens,
  sum_reasoning_tokens,
  sum_input_tokens + sum_output_tokens + sum_reasoning_tokens AS total_tokens,
  ROUND((last_log_nano - first_log_nano) / 1000000.0, 3) AS log_span_coarse_ms,
  first_log_nano,
  last_log_nano,
  sample_trace_id
FROM per_invocation
ORDER BY first_log_nano DESC;
