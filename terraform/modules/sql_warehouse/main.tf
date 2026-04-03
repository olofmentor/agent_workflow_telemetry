resource "databricks_sql_endpoint" "this" {
  name             = var.name
  cluster_size     = var.cluster_size
  min_num_clusters = var.min_num_clusters
  max_num_clusters = var.max_num_clusters
  auto_stop_mins   = var.auto_stop_mins
  warehouse_type = var.warehouse_type
  enable_photon  = var.enable_photon
}

resource "databricks_permissions" "warehouse" {
  count = var.enable_group_permissions && length(var.group_permission_levels) > 0 ? 1 : 0

  sql_endpoint_id = databricks_sql_endpoint.this.id

  dynamic "access_control" {
    for_each = var.group_permission_levels
    content {
      group_name       = access_control.key
      permission_level = access_control.value
    }
  }
}
