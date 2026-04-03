output "catalog_name" {
  value       = databricks_catalog.this.name
  description = "Catalog name; pass to uc_mlflow_trace_schema and agent DATABRICKS_CATALOG."
}

output "catalog_id" {
  value       = databricks_catalog.this.id
  description = "Unity Catalog resource id from the provider."
}
