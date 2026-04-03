output "warehouse_id" {
  value       = databricks_sql_endpoint.this.id
  description = "Warehouse id (UUID). Set MLFLOW_TRACING_SQL_WAREHOUSE_ID in agent / init environment."
}

output "warehouse_name" {
  value       = databricks_sql_endpoint.this.name
  description = "Warehouse display name."
}

