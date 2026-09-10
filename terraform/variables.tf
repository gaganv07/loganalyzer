variable "supabase_access_token" {
  description = "Supabase Management API Personal Access Token"
  type        = string
  sensitive   = true
  default     = ""
}

variable "supabase_url" {
  description = "Supabase Project URL"
  type        = string
  default     = "https://your-project-id.supabase.co"
}

variable "bucket_name" {
  description = "Name of the Supabase Storage bucket dedicated to log processing"
  type        = string
  default     = "application-logs"
}
