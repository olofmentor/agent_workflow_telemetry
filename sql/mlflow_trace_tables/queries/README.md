# Example analytics queries

Run these in a Databricks SQL warehouse or notebook against your UC trace schema. Replace `` `dev_ai`.`agent_traces` `` if your catalog/schema differ.

| File | Purpose |
|------|---------|
| [`agent_session_metrics_by_agent.sql`](agent_session_metrics_by_agent.sql) | Sessions, total tokens, and average session wall time **per agent** (from OTLP logs + session bounds). |
| [`trace_steps_inputs_outputs.sql`](trace_steps_inputs_outputs.sql) | Ordered span steps for one `trace_id` with common input/output attribute columns. |
| [`list_trace_ids_for_session.sql`](list_trace_ids_for_session.sql) | Map `session_id` (ADK) to recent `trace_id` values from spans (helper). |

### Semantics

- **Agent sessions** = distinct `session_id` values where at least one log row carries that `agent_name` (see `observability/session_logs.py`: `agent_name`, `session_id` on OTLP log attributes).
- **Tokens** = sum of `input_tokens`, `output_tokens`, and `reasoning_token_count` on rows with `event_type = 'agent.llm_step'`. Values are stored as strings in `attributes`; the query uses `TRY_CAST`.
- **Average time per session** = average **wall-clock span** of the whole session: `(max - min) time_unix_nano` across all sampled log rows in that session, **in milliseconds**, then averaged over sessions where the agent appears. This includes idle gaps between invocations; adjust the time bounds in SQL if you need per-invocation latency instead.

If log attribute keys differ in your exporter version, inspect one row:  
`SELECT attributes FROM ... LIMIT 1`.
