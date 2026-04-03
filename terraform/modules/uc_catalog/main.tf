resource "databricks_catalog" "this" {
  name           = var.catalog_name
  comment        = var.comment
  storage_root   = var.storage_root
  isolation_mode = var.isolation_mode
}

resource "databricks_grants" "catalog" {
  count = var.enable_catalog_grants && length(var.catalog_grants) > 0 ? 1 : 0

  catalog = databricks_catalog.this.name

  dynamic "grant" {
    for_each = var.catalog_grants
    content {
      principal  = grant.value.principal
      privileges = grant.value.privileges
    }
  }
}
