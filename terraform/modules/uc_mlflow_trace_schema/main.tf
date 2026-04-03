resource "databricks_schema" "mlflow_traces" {
  catalog_name = var.catalog_name
  name         = var.schema_name
  comment      = var.schema_comment
}

resource "databricks_grants" "schema" {
  count = var.enable_schema_grants && length(var.schema_grants) > 0 ? 1 : 0

  schema = databricks_schema.mlflow_traces.id

  dynamic "grant" {
    for_each = var.schema_grants
    content {
      principal  = grant.value.principal
      privileges = grant.value.privileges
    }
  }
}
