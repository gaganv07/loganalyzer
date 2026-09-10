# Terraform Infrastructure Configuration for Supabase Storage

This folder contains Terraform configuration files to automate the creation of the Supabase Storage bucket (`application-logs`).

## Prerequisites

1. [Terraform CLI](https://www.terraform.io/downloads.html) installed (version >= 1.0.0).
2. A Supabase Project created via [Supabase Dashboard](https://supabase.com).
3. A Supabase Personal Access Token (generated from **Supabase Account Settings -> Access Tokens**).

## Execution Steps

### 1. Initialize Terraform
```bash
cd terraform
terraform init
```

### 2. Preview Infrastructure Plan
```bash
terraform plan -var="supabase_access_token=YOUR_SUPABASE_ACCESS_TOKEN"
```

### 3. Apply Infrastructure Changes
```bash
terraform apply -var="supabase_access_token=YOUR_SUPABASE_ACCESS_TOKEN"
```

## Manual Supabase Dashboard Fallback

If you prefer not to create a Personal Access Token or if your project permissions restrict Management API usage:

1. Open your project in the [Supabase Dashboard](https://supabase.com/dashboard).
2. Navigate to **Storage** from the left navigation panel.
3. Click **New Bucket**.
4. Enter `application-logs` as the Bucket Name.
5. Set bucket privacy settings (Private or Public based on your security policies).
6. Click **Save**.
