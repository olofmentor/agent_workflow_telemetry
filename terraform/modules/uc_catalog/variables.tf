variable "catalog_name" {
  type        = string
  description = "Name of the Unity Catalog to create."
}

variable "storage_root" {
  type        = string
  description = "Cloud storage URI for managed tables (e.g. abfss://...@... or s3://...). Required for new catalogs."
}

variable "comment" {
  type        = string
  default     = "Application-managed Unity Catalog"
  description = "Catalog description."
}

variable "isolation_mode" {
  type        = string
  description = "OPEN or ISOLATED; see Databricks Unity Catalog docs."
  default     = "ISOLATED"
}

variable "catalog_grants" {
  type = list(object({
    principal  = string
    privileges = list(string)
  }))
  description = "Optional grants at catalog level (e.g. USE_CATALOG for application groups)."
  default     = []
}

variable "enable_catalog_grants" {
  type    = bool
  default = true
}
