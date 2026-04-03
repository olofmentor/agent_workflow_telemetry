variable "name" {
  type        = string
  description = "SQL warehouse name (visible in workspace)."
}

variable "cluster_size" {
  type        = string
  description = "Warehouse t-shirt size (see provider docs for allowed values on your workspace)."
  default     = "Small"
}

variable "min_num_clusters" {
  type        = number
  description = "Minimum running clusters."
  default     = 1
}

variable "max_num_clusters" {
  type        = number
  description = "Maximum concurrent clusters."
  default     = 1
}

variable "auto_stop_mins" {
  type        = number
  description = "Minutes of idle time before the warehouse stops."
  default     = 30
}

variable "warehouse_type" {
  type        = string
  description = "PRO or CLASSIC depending on workspace capabilities."
  default     = "PRO"
}

variable "enable_photon" {
  type    = bool
  default = true
}

variable "group_permission_levels" {
  type        = map(string)
  description = "Map of Databricks group display name -> permission_level (e.g. CAN_USE, IS_OWNER)."
  default     = {}
}

variable "enable_group_permissions" {
  type        = bool
  description = "Set false to manage warehouse ACLs outside Terraform."
  default     = true
}
