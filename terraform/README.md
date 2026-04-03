# Terraform: Databricks resources for agent tracing

These modules provision **Databricks infrastructure** that complements the Python `init` package:

| What Terraform creates | What stays in Python / MLflow API |
|------------------------|-----------------------------------|
| Unity Catalog **schema** for trace storage (empty of OTEL tables initially) | Calling `set_experiment_trace_location` / `python -m init` creates **MLflow experiment** and **UC OTEL tables** (`mlflow_experiment_trace_otel_*`) |
| **SQL warehouse** for `MLFLOW_TRACING_SQL_WAREHOUSE_ID` | Experiment id and OTLP headers still come from `init` after linking |

### Terraform output → environment variables → `init`

| Terraform / workspace output | Typical `.env` variable | Used by |
|------------------------------|-------------------------|---------|
| `warehouse_id` (SQL warehouse resource) | `MLFLOW_TRACING_SQL_WAREHOUSE_ID` | `init.ensure_trace_infrastructure`, MLflow `set_experiment_trace_location` |
| `catalog_name` / first part of `trace_schema_full_name` | `DATABRICKS_CATALOG` | `init` UC location + agent scripts |
| `schema_name` / second part of `trace_schema_full_name` | `DATABRICKS_SCHEMA` | `init` UC location (default `mlflow_traces`) |
| Workspace URL | `DATABRICKS_HOST` | Optional: derive `OTEL_EXPORTER_OTLP_ENDPOINT` when unset |
| PAT / SP token | `DATABRICKS_TOKEN` (or `Authorization` in headers) | `init.build_trace_configuration_updates` |

After `apply`, set the first three in `.env`, then run `python -m init` to create/link the MLflow experiment and refresh `OTEL_EXPORTER_OTLP_HEADERS` (experiment id + `X-Databricks-UC-Table-Name`). Then start the agent so [`observability/otel_sdk.py`](../observability/otel_sdk.py) reads those variables.

## Modules

| Path | Purpose |
|------|---------|
| [`modules/uc_catalog`](modules/uc_catalog) | Optional **managed catalog** + optional catalog-level grants (requires `storage_root` on your cloud). |
| [`modules/uc_mlflow_trace_schema`](modules/uc_mlflow_trace_schema) | **Schema** inside an existing catalog (`catalog_name` + `schema_name`) + optional `databricks_grants`. |
| [`modules/sql_warehouse`](modules/sql_warehouse) | **SQL warehouse** + optional group permissions (`group_permission_levels` map). |
| [`modules/stack_agent_tracing`](modules/stack_agent_tracing) | Opinionated **composition**: trace schema + warehouse (typical for this repo). |

## Example

[`examples/agent_tracing`](examples/agent_tracing) wires `stack_agent_tracing` with workspace provider configuration:

```bash
cd terraform/examples/agent_tracing
cp terraform.tfvars.example terraform.tfvars
# edit terraform.tfvars
terraform init
terraform plan
terraform apply
```

Copy outputs `warehouse_id` and `trace_schema_full_name` into your agent `.env` (`MLFLOW_TRACING_SQL_WAREHOUSE_ID`, `DATABRICKS_CATALOG`, `DATABRICKS_SCHEMA`). Then run `python -m init` (or your app with `AUTO_CONFIGURE_DATABRICKS_TRACING`) to link the experiment and create OTEL tables.

## Provider authentication

The examples use `host` + `token`. Many teams instead use:

- `ARM_*` variables for Azure-managed identity, or  
- Account-level provider configuration (see [Databricks Terraform provider](https://registry.terraform.io/providers/databricks/databricks/latest/docs)).

Adjust the `provider "databricks"` block to match your platform standard.

## Version notes

- Provider constraint: `>= 1.36.0` (bump if your workspace requires a newer provider).
- UC **privilege** strings and SQL **warehouse sizes** can vary by region and account; adjust grants and `cluster_size` if `plan`/`apply` returns API errors.
- If `databricks_grants` syntax differs in your provider version, manage grants via Databricks SQL or account console and set `enable_schema_grants = false` / `enable_catalog_grants = false`.

## Compose with a new catalog

```hcl
module "catalog" {
  source         = "../modules/uc_catalog"
  catalog_name   = "dev_agent"
  storage_root   = var.databricks_storage_root
  catalog_grants = [...]
}

module "tracing" {
  source       = "../modules/stack_agent_tracing"
  catalog_name = module.catalog.catalog_name
  ...
}
```
