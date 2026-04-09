-- Resolve ADK session_id → trace_id values on spans (via gen_ai.conversation.id; see readme-logs.md).
-- Paste a value into params, then use trace_id in trace_steps_inputs_outputs.sql.

WITH params AS (
  SELECT 'REPLACE_WITH_SESSION_ID' AS session_id
)

SELECT DISTINCT
  s.trace_id,
  MIN(s.start_time_unix_nano) AS first_span_nano,
  MAX(s.end_time_unix_nano) AS last_span_nano,
  COUNT(*) AS span_count
FROM `dev_ai`.`agent_traces`.`mlflow_experiment_trace_otel_spans` s
CROSS JOIN params p
WHERE s.attributes['gen_ai.conversation.id'] = p.session_id
GROUP BY s.trace_id
ORDER BY first_span_nano DESC;
