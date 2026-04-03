provider "databricks" {
  host  = var.databricks_host
  token = var.databricks_token
}

module "agent_tracing" {
  source = "../../modules/stack_agent_tracing"

  catalog_name = var.catalog_name
  schema_name  = var.schema_name

  warehouse_name         = var.warehouse_name
  warehouse_cluster_size = "Small"

  schema_grants        = var.trace_schema_grants
  enable_schema_grants = length(var.trace_schema_grants) > 0

  warehouse_group_permission_levels  = var.warehouse_group_permission_levels
  enable_warehouse_group_permissions = length(var.warehouse_group_permission_levels) > 0
}

output "warehouse_id" {
  value       = module.agent_tracing.warehouse_id
  description = "MLFLOW_TRACING_SQL_WAREHOUSE_ID"
}

output "trace_schema_full_name" {
  value       = module.agent_tracing.trace_schema_full_name
  description = "DATABRICKS_CATALOG / DATABRICKS_SCHEMA for Python init"
}
