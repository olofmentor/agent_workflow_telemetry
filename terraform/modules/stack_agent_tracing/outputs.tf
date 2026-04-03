output "warehouse_id" {
  value       = module.sql_warehouse.warehouse_id
  description = "Set MLFLOW_TRACING_SQL_WAREHOUSE_ID to this value."
}

output "trace_schema_full_name" {
  value       = module.uc_mlflow_trace_schema.schema_full_name
  description = "Use as DATABRICKS_CATALOG.DATABRICKS_SCHEMA when calling init / set_experiment_trace_location."
}

output "catalog_name" {
  value = module.uc_mlflow_trace_schema.catalog_name
}

output "schema_name" {
  value = module.uc_mlflow_trace_schema.schema_name
}
