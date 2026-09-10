output "bucket_name" {
  description = "Name of the provisioned Supabase storage bucket"
  value       = var.bucket_name
}

output "storage_folder_logs" {
  description = "Remote storage location path for log files"
  value       = "${var.bucket_name}/logs/"
}

output "storage_folder_reports" {
  description = "Remote storage location path for summary report files"
  value       = "${var.bucket_name}/reports/"
}
