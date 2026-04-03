variable "databricks_host" {
  type        = string
  description = "Workspace URL without trailing slash, e.g. https://adb-xxxx.azuredatabricks.net"
}

variable "databricks_token" {
  type        = string
  sensitive   = true
  description = "Personal access token or service principal token for workspace API."
}

variable "catalog_name" {
  type        = string
  description = "Existing Unity Catalog (create separately or use terraform/modules/uc_catalog)."
  default     = "main"
}

variable "schema_name" {
  type    = string
  default = "mlflow_traces"
}

variable "warehouse_name" {
  type        = string
  description = "SQL warehouse for trace setup / SQL queries against trace tables."
  default     = "agent-genai-tracing"
}

variable "trace_schema_grants" {
  type = list(object({
    principal  = string
    privileges = list(string)
  }))
  description = "Example: [{ principal = \"data_engineers\", privileges = [\"USE_SCHEMA\", \"SELECT\"] }]"
  default     = []
}

variable "warehouse_group_permission_levels" {
  type        = map(string)
  description = "Databricks group display name -> warehouse permission (e.g. { engineers = \"CAN_USE\" })."
  default     = {}
}
