module "uc_mlflow_trace_schema" {
  source = "../uc_mlflow_trace_schema"

  catalog_name         = var.catalog_name
  schema_name          = var.schema_name
  schema_grants        = var.schema_grants
  enable_schema_grants = var.enable_schema_grants
}

module "sql_warehouse" {
  source = "../sql_warehouse"

  name                     = var.warehouse_name
  cluster_size             = var.warehouse_cluster_size
  group_permission_levels  = var.warehouse_group_permission_levels
  enable_group_permissions = var.enable_warehouse_group_permissions
}
