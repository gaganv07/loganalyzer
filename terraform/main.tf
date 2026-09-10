terraform {
  required_version = ">= 1.0.0"
  required_providers {
    supabase = {
      source  = "supabase/supabase"
      version = "~> 1.0"
    }
  }
}

provider "supabase" {
  access_token = var.supabase_access_token
}

# Supabase Storage Bucket Resource
resource "supabase_bucket" "application_logs" {
  bucket_id          = var.bucket_name
  name               = var.bucket_name
  public             = false
  file_size_limit    = 10485760 # 10MB limit
  allowed_mime_types = ["text/plain", "application/json", "text/log"]
}
