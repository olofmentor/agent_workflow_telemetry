# Unity Catalog Table Setup for OpenTelemetry Traces

## Overview
This directory contains SQL scripts to create Unity Catalog tables for storing OpenTelemetry traces from the agent workflow.

## Files
- **`create_otel_traces_simple.sql`** - Recommended: Standard Databricks OTEL table format
- **`create_traces_table.sql`** - Extended version with additional custom fields

## Quick Setup

### Step 1: Run the DDL in Databricks

1. Open your Databricks workspace: https://adb-957977613266276.16.azuredatabricks.net
2. Go to **SQL Editor** or create a new **Notebook**
3. Copy and paste the contents of `create_otel_traces_simple.sql`
4. Run the script

### Step 2: Verify Table Creation

```sql
-- Check if table exists
SHOW TABLES IN main.agent_traces;

-- View table schema
DESCRIBE TABLE EXTENDED main.agent_traces.otel_traces;

-- Verify permissions
SHOW GRANTS ON TABLE main.agent_traces.otel_traces;
```

### Step 3: Configure Environment

The `.env` file has been updated to use the new table:
```
X-Databricks-UC-Table-Name=main.agent_traces.otel_traces
```

### Step 4: Test the Setup

Run the test script to verify traces can be exported:

```bash
python3 test_otlp_export.py
```

Expected output: `✓ Trace sent and flushed` (without error messages)

### Step 5: Run the Workflow

```bash
./run_with_traces.sh
```

### Step 6: View Traces in Databricks

**Option A: Query the table directly**
```sql
SELECT 
  trace_id,
  span_id,
  name,
  service_name,
  start_time,
  end_time,
  TIMESTAMPDIFF(MILLISECOND, start_time, end_time) as duration_ms
FROM main.agent_traces.otel_traces
ORDER BY start_time DESC
LIMIT 100;
```

**Option B: View in MLflow UI**
- Go to: https://adb-957977613266276.16.azuredatabricks.net/ml/experiments/3078644569850998/traces
- Traces should appear within 1-2 minutes

## Troubleshooting

### Permission Errors (403)
If you get permission errors, ask your Databricks admin to run:

```sql
GRANT USE CATALOG ON CATALOG main TO `your.email@domain.com`;
GRANT USE SCHEMA ON SCHEMA main.agent_traces TO `your.email@domain.com`;
GRANT SELECT, MODIFY ON TABLE main.agent_traces.otel_traces TO `your.email@domain.com`;
```

### Table Not Found (404)
Verify the table exists:
```sql
SHOW TABLES IN main.agent_traces LIKE 'otel_traces';
```

### Traces Not Appearing
1. Check table for recent data:
   ```sql
   SELECT COUNT(*), MAX(_ingestion_time) 
   FROM main.agent_traces.otel_traces;
   ```

2. Verify environment variables:
   ```bash
   grep OTEL .env
   ```

3. Check for export errors:
   ```bash
   python3 test_otlp_export.py 2>&1 | grep -i error
   ```

## Table Schema

The `main.agent_traces.otel_traces` table follows the standard Databricks OpenTelemetry format:

| Column | Type | Description |
|--------|------|-------------|
| `trace_id` | STRING | Unique identifier for the entire trace |
| `span_id` | STRING | Unique identifier for this span |
| `parent_span_id` | STRING | Parent span ID (null for root spans) |
| `name` | STRING | Operation name |
| `kind` | STRING | Span kind (INTERNAL, CLIENT, SERVER, etc.) |
| `start_time` | TIMESTAMP | When the span started |
| `end_time` | TIMESTAMP | When the span ended |
| `attributes` | MAP<STRING, STRING> | Span attributes (key-value pairs) |
| `events` | ARRAY<STRUCT> | Span events with timestamps |
| `status_code` | STRING | Status (OK, ERROR, UNSET) |
| `resource_attributes` | MAP<STRING, STRING> | Service/resource attributes |

## Advanced: Custom Table Schema

If you need additional fields (workflow_id, agent_name, etc.), use `create_traces_table.sql` instead. This provides a more structured schema with explicit columns for agent-specific metadata.

## Contact

If you need help with:
- Unity Catalog permissions → Contact your Databricks admin
- Table schema changes → Modify the SQL files
- Workflow issues → Check the main README.md
