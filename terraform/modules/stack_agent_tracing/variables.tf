variable "catalog_name" {
  type        = string
  description = "Existing UC catalog where the trace schema will live."
}

variable "schema_name" {
  type        = string
  default     = "mlflow_traces"
  description = "UC schema for MLflow GenAI traces (matches DATABRICKS_SCHEMA)."
}

variable "schema_grants" {
  type = list(object({
    principal  = string
    privileges = list(string)
  }))
  default     = []
  description = "Optional schema grants; see uc_mlflow_trace_schema module."
}

variable "enable_schema_grants" {
  type    = bool
  default = true
}

variable "warehouse_name" {
  type        = string
  description = "Name of the SQL warehouse used for MLFLOW_TRACING_SQL_WAREHOUSE_ID."
}

variable "warehouse_cluster_size" {
  type    = string
  default = "Small"
}

variable "warehouse_group_permission_levels" {
  type        = map(string)
  default     = {}
  description = "Databricks group -> permission on warehouse (typically CAN_USE)."
}

variable "enable_warehouse_group_permissions" {
  type    = bool
  default = true
}
