variable "supabase_access_token" {
  description = "Supabase Management API Personal Access Token"
  type        = string
  sensitive   = true
}

variable "project_ref" {
  description = "Supabase project reference ID"
  type        = string
}

variable "bucket_name" {
  description = "Name of the Supabase Storage bucket"
  type        = string
  default = "terraform-application-logs"
}