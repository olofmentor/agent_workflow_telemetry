-- Metrics by agent: session count, total tokens (LLM steps), avg session wall time.
-- Replace catalog/schema if needed.
--
-- Optional filters (uncomment):
--   AND time_unix_nano >= UNIX_TIMESTAMP(TO_TIMESTAMP('2026-02-01')) * 1e9

WITH log_rows AS (
  SELECT
    attributes['agent_name'] AS agent_name,
    attributes['session_id'] AS session_id,
    attributes['event_type'] AS event_type,
    TRY_CAST(NULLIF(TRIM(attributes['input_tokens']), '') AS BIGINT) AS input_tokens,
    TRY_CAST(NULLIF(TRIM(attributes['output_tokens']), '') AS BIGINT) AS output_tokens,
    TRY_CAST(NULLIF(TRIM(attributes['reasoning_token_count']), '') AS BIGINT) AS reasoning_tokens,
    time_unix_nano
  FROM `dev_ai`.`agent_traces`.`mlflow_experiment_trace_otel_logs`
  WHERE attributes['agent_name'] IS NOT NULL
    AND TRIM(attributes['agent_name']) != ''
),

-- Wall time per ADK session (first → last log timestamp in that session).
session_wall AS (
  SELECT
    session_id,
    (MAX(time_unix_nano) - MIN(time_unix_nano)) / 1000000.0 AS session_wall_ms
  FROM log_rows
  WHERE session_id IS NOT NULL AND TRIM(session_id) != ''
  GROUP BY session_id
),

-- Sessions in which each agent appeared at least once.
agent_to_sessions AS (
  SELECT DISTINCT agent_name, session_id
  FROM log_rows
  WHERE session_id IS NOT NULL AND TRIM(session_id) != ''
),

agent_session_times AS (
  SELECT
    a.agent_name,
    a.session_id,
    w.session_wall_ms
  FROM agent_to_sessions a
  JOIN session_wall w ON a.session_id = w.session_id
),

token_totals AS (
  SELECT
    agent_name,
    SUM(
      COALESCE(input_tokens, 0)
      + COALESCE(output_tokens, 0)
      + COALESCE(reasoning_tokens, 0)
    ) AS total_tokens
  FROM log_rows
  WHERE event_type = 'agent.llm_step'
  GROUP BY agent_name
)

SELECT
  s.agent_name,
  COUNT(DISTINCT s.session_id) AS agent_sessions,
  COALESCE(MAX(t.total_tokens), 0) AS total_tokens_used,
  ROUND(AVG(s.session_wall_ms), 3) AS avg_session_wall_ms,
  ROUND(MIN(s.session_wall_ms), 3) AS min_session_wall_ms,
  ROUND(MAX(s.session_wall_ms), 3) AS max_session_wall_ms
FROM agent_session_times s
LEFT JOIN token_totals t ON s.agent_name = t.agent_name
GROUP BY s.agent_name
ORDER BY agent_sessions DESC, s.agent_name;
