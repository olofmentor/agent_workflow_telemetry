variable "catalog_name" {
  type        = string
  description = "Existing Unity Catalog name (e.g. main, dev_ai). The catalog must already exist unless you use the optional uc_catalog module."
}

variable "schema_name" {
  type        = string
  description = "Schema that will hold MLflow GenAI trace OTEL tables (created later by MLflow set_experiment_trace_location)."
  default     = "mlflow_traces"
}

variable "schema_comment" {
  type        = string
  description = "Comment stored on the UC schema."
  default     = "MLflow GenAI / OpenTelemetry trace storage. OTEL tables are created when linking an experiment via set_experiment_trace_location."
}

variable "schema_grants" {
  type = list(object({
    principal  = string
    privileges = list(string)
  }))
  description = <<-EOT
    Optional UC grants on this schema (e.g. CAN_USE for groups that run the agent or admins who query traces).
    Typical privileges: USE_SCHEMA, SELECT, MODIFY (adjust to your governance model).
    Principals can be group names or service principal application IDs depending on workspace settings.
  EOT
  default     = []
}

variable "enable_schema_grants" {
  type        = bool
  description = "Set false to manage grants outside Terraform (e.g. account-level IAM)."
  default     = true
}
