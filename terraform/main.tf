terraform {
  required_version = ">= 1.0.0"

  required_providers {
    supabase = {
      source  = "shellscape/supabase"
      version = "~> 0.1"
    }
  }
}

provider "supabase" {
  access_token = var.supabase_access_token
}

resource "supabase_storage_bucket" "application_logs" {
  project_ref        = var.project_ref
  name               = var.bucket_name
  public             = false
  file_size_limit    = 10485760
  allowed_mime_types = [
    "text/plain",
    "application/json",
    "text/log"
  ]
}