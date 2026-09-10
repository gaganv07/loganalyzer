$ErrorActionPreference = "Stop"

$projectRef = $env:TF_VAR_project_ref
$bucketName = "terraform-application-logs"
$filePath = "D:\cloudassignmentnewgagan\logs\application.log"
$objectPath = "logs/application.log"

if (-not $projectRef) {
    throw "TF_VAR_project_ref is not set."
}

if (-not $env:SUPABASE_SERVICE_ROLE_KEY) {
    throw "SUPABASE_SERVICE_ROLE_KEY is not set."
}

if (-not (Test-Path $filePath)) {
    throw "Log file not found: $filePath"
}

$url = "https://$projectRef.supabase.co/storage/v1/object/$bucketName/$objectPath"

$headers = @{
    "Authorization" = "Bearer $env:SUPABASE_SERVICE_ROLE_KEY"
    "apikey"        = $env:SUPABASE_SERVICE_ROLE_KEY
}

Write-Host "Uploading application.log to Supabase..."

Invoke-RestMethod `
    -Uri $url `
    -Method Post `
    -Headers $headers `
    -ContentType "text/plain" `
    -InFile $filePath

Write-Host "Upload completed successfully."
Write-Host "Bucket: $bucketName"
Write-Host "Object: $objectPath"