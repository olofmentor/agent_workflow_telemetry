output "schema_id" {
  value       = databricks_schema.mlflow_traces.id
  description = "Unity Catalog schema id (catalog.schema), suitable for grants and references."
}

output "schema_full_name" {
  value       = "${var.catalog_name}.${var.schema_name}"
  description = "Fully qualified schema name; set DATABRICKS_CATALOG / DATABRICKS_SCHEMA in the agent env to match."
}

output "catalog_name" {
  value = var.catalog_name
}

output "schema_name" {
  value = var.schema_name
}
