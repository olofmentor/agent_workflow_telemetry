-- Root-span traces in ERROR state (mlflow_experiment_trace_unified normalizes status.code).
-- Use for ops: recent failed GenAI traces with coalesced request/response fields.

SELECT
  trace_id,
  request_time,
  state,
  execution_duration_ms,
  request,
  response,
  trace_metadata
FROM `dev_ai`.`agent_traces`.`mlflow_experiment_trace_unified`
WHERE state = 'ERROR'
ORDER BY request_time DESC
LIMIT 500;
