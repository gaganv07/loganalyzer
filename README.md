# Log Analyzer: Cloud Application Log Processing & Summary Generator

A complete, production-ready Python application designed for cloud log analysis. The system uploads application log files to **Supabase Cloud Storage**, retrieves and parses log entries, counts log levels (`INFO`, `WARNING`/`WARN`, `ERROR`, `DEBUG`, and `Malformed`), groups repeated error and warning patterns, computes key statistics, generates structured **JSON** and human-readable **TXT** summary reports, uploads the reports back to cloud storage, and includes infrastructure-as-code with **Terraform**.

---

## 1. Project Title
**Log Analyzer: Process Application Logs Stored in Cloud Storage and Generate Summaries of Errors or Warnings**

---

## 2. Problem Statement
Modern cloud applications generate high volumes of log files across distributed servers. Manually inspecting raw log files to identify recurring application failures, system warnings, or service bottlenecks is inefficient and error-prone. Organizations require an automated log pipeline to process raw log data stored in cloud storage, aggregate error metrics, and produce actionable summary reports.

---

## 3. Objective
- Automatically ingest application log files into Supabase Cloud Storage.
- Download and parse log entries using robust regular expression pattern matching.
- Categorize entries into `INFO`, `WARNING`, `ERROR`, `DEBUG`, and `Malformed` lines without crashing.
- Aggregate repeated error and warning messages to identify root cause trends.
- Calculate total counts, percentages, and identify most frequent error and warning messages.
- Export findings into structured `summary.json` and formatted `summary.txt` report files.
- Upload generated summary reports back to Supabase Cloud Storage.
- Automate cloud infrastructure setup using Terraform.

---

## 4. Features
- **Cloud Storage Integration**: Full integration with Supabase Storage for seamless file uploads and downloads.
- **Robust Log Parsing**: Flexibly handles timestamps, log levels (`INFO`, `WARNING`, `WARN`, `ERROR`, `DEBUG`), and line formats.
- **Graceful Error Handling**: Captures malformed log lines as `Malformed` entries without crashing the application.
- **Statistical Aggregation**: Automatically computes percentages, unique error/warning totals, and ranks most frequent messages.
- **Dual Format Reports**: Produces machine-readable `summary.json` and clean `summary.txt` text summaries.
- **Strict Error Detection**: Fails loudly if a cloud upload/download fails, providing explicit execution status breakdowns.
- **Automated Infrastructure**: Includes complete Terraform manifests (`main.tf`, `variables.tf`, `outputs.tf`) for bucket provisioning.
- **Comprehensive Unit Testing**: Includes unit tests covering log parsing, metrics calculation, duplicate message grouping, and report output generation.

---

## 5. Architecture & Data Flow

```
Application Log (logs/application.log)
          ↓
Supabase Storage (application-logs/logs/application.log)
          ↓
Python Log Analyzer (analyzer/log_parser.py & log_analyzer.py)
          ↓
Parse Logs (INFO / WARNING / ERROR / DEBUG / Malformed)
          ↓
Detect & Group ERROR/WARNING Patterns
          ↓
Generate Summary Reports (analyzer/report_generator.py)
          ↓
JSON (reports/summary.json) & TXT (reports/summary.txt)
          ↓
Upload Summary Reports to Supabase Storage (application-logs/reports/...)
```

---

## 6. Technologies Used
- **Python 3.11+**: Core processing and logic implementation.
- **Supabase Storage / Supabase Python Client**: Cloud storage repository for logs and summary artifacts.
- **Terraform (HCL)**: Infrastructure as Code for automated cloud bucket management.
- **Python Standard Library & Dataclasses**: `re`, `collections.Counter`, `dataclasses`, `json`, `unittest`.
- **python-dotenv**: Local environment variable management.

---

## 7. Project Structure

```
log-analyzer/
│
├── analyzer/
│   ├── __init__.py           # Package marker
│   ├── log_analyzer.py       # Log statistics calculation & message grouping
│   ├── log_parser.py         # Regex parsing and line normalization
│   ├── report_generator.py   # JSON & TXT summary file creation
│   └── supabase_storage.py   # Supabase Storage client wrapper
│
├── logs/
│   └── application.log       # Sample application log file
│
├── reports/
│   ├── .gitkeep              # Folder placeholder
│   ├── summary.json          # Generated JSON summary report
│   └── summary.txt           # Generated TXT text summary report
│
├── terraform/
│   ├── main.tf               # Terraform bucket resource configuration
│   ├── variables.tf          # Variable declarations
│   ├── outputs.tf            # Output definitions
│   └── README.md             # Infrastructure setup documentation
│
├── tests/
│   ├── __init__.py           # Test package marker
│   └── test_log_analyzer.py  # Unit test suite
│
├── .env.example              # Template for environment credentials
├── .gitignore                # Excludes secrets, bytecode, and state files
├── requirements.txt          # Python dependencies
├── main.py                   # Main CLI execution entry point
└── README.md                 # Project documentation
```

---

## 8. Supabase Setup & Storage Bucket
1. Create a free account at [Supabase](https://supabase.com) and create a project.
2. The storage bucket **`application-logs`** is **PRIVATE** by default.
3. The Python application performs server-side storage operations.

---

## 9. Resolving Supabase Storage 403 / RLS Permission Errors

If you encounter `403 Unauthorized` or `new row violates row-level security policy` during `python main.py`, choose **Option A** or **Option B**:

### Option A: Use Service Role Secret Key (RECOMMENDED for Python Backend)
The `service_role` key bypasses Row Level Security (RLS) policies for administrative server tasks.
1. In Supabase Dashboard, navigate to **Project Settings -> API**.
2. Copy the **`service_role` secret key** (under Project API Keys).
3. In your local `.env` file, set:
   ```env
   SUPABASE_SERVICE_ROLE_KEY=your_actual_service_role_key_here
   ```

### Option B: Apply Storage RLS Policies for Public/Anon Key
If using the standard public `anon` key (`SUPABASE_KEY`), you must run the following SQL script in **Supabase Dashboard -> SQL Editor** to grant permission specifically for `application-logs`:

```sql
-- Storage RLS Policies for 'application-logs' bucket
CREATE POLICY "Allow select on application-logs bucket"
ON storage.objects FOR SELECT
TO public, anon, authenticated, service_role
USING (bucket_id = 'application-logs');

CREATE POLICY "Allow insert on application-logs bucket"
ON storage.objects FOR INSERT
TO public, anon, authenticated, service_role
WITH CHECK (bucket_id = 'application-logs');

CREATE POLICY "Allow update on application-logs bucket"
ON storage.objects FOR UPDATE
TO public, anon, authenticated, service_role
USING (bucket_id = 'application-logs')
WITH CHECK (bucket_id = 'application-logs');

CREATE POLICY "Allow delete on application-logs bucket"
ON storage.objects FOR DELETE
TO public, anon, authenticated, service_role
USING (bucket_id = 'application-logs');
```

---

## 10. Environment Variable Setup

Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

Edit `.env` and fill in your credentials:

```env
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your-supabase-service-role-key
# OR
SUPABASE_KEY=your-supabase-anon-key
SUPABASE_BUCKET=application-logs
```

> **Security Requirement**: All credentials MUST be stored in `.env`. `.env` is listed in `.gitignore` and MUST NEVER be committed to GitHub.

---

## 11. Installing Python Dependencies

```bash
pip install -r requirements.txt
```

---

## 12. Terraform Setup
Navigating to `terraform/` allows you to manage cloud infrastructure declaratively using [Terraform CLI](https://www.terraform.io/downloads.html).

---

## 13. Running Terraform

```bash
cd terraform
terraform init
terraform plan -var="supabase_access_token=YOUR_SUPABASE_ACCESS_TOKEN"
terraform apply -var="supabase_access_token=YOUR_SUPABASE_ACCESS_TOKEN"
```

---

## 14. Running the Log Analyzer

Run the main CLI script from the project root directory:

```bash
python main.py
```

---

## 15. Example Terminal Output

```text
========================================
       LOG ANALYZER PROCESS APP         
========================================

Connecting to Supabase...
Connected successfully to Supabase Storage.

Uploading 'logs/application.log' to Supabase Storage path 'logs/application.log'...
Upload successful.

Downloading log file from Supabase Storage path 'logs/application.log'...
Download successful.

Processing logs...

Analysis completed.
----------------------------------------
Total Logs : 25
Errors     : 8 (32.0%)
Warnings   : 7 (28.0%)
Info       : 8
Debug      : 1
Malformed  : 1
----------------------------------------
Most Frequent Error   : Database connection failed: network timeout reaching db.internal
Most Frequent Warning : Database response slow
----------------------------------------

Generating reports...
[OK] reports\summary.json created
[OK] reports\summary.txt created

Uploading reports to Supabase Storage...
[OK] logs/summary.json uploaded successfully.
[OK] logs/summary.txt uploaded successfully.
Reports uploaded successfully to Supabase Storage.

========================================
       EXECUTION STATUS BREAKDOWN       
========================================
Supabase Connection : SUCCESS
Log Upload          : SUCCESS
Log Download        : SUCCESS
Log Analysis        : SUCCESS
Report Generation   : SUCCESS
Report Upload       : SUCCESS
========================================
        EXECUTION COMPLETED             
========================================
```

---

## 16. Report Format

### `reports/summary.json`
```json
{
  "analysis": {
    "total_entries": 25,
    "info": 8,
    "warnings": 7,
    "errors": 8,
    "debug": 1,
    "malformed": 1,
    "unique_errors": 3,
    "unique_warnings": 3,
    "error_percentage": 32.0,
    "warning_percentage": 28.0
  },
  "errors": [
    {
      "message": "Database connection failed: network timeout reaching db.internal",
      "count": 4
    },
    {
      "message": "File upload failed: permission denied for bucket application-logs",
      "count": 2
    },
    {
      "message": "Authentication failed: invalid token signature for user_502",
      "count": 2
    }
  ],
  "warnings": [
    {
      "message": "Database response slow",
      "count": 3
    },
    {
      "message": "Memory usage high",
      "count": 3
    },
    {
      "message": "Cache miss ratio high",
      "count": 1
    }
  ],
  "most_frequent_error": "Database connection failed: network timeout reaching db.internal",
  "most_frequent_warning": "Database response slow"
}
```

### `reports/summary.txt`
```text
LOG ANALYSIS SUMMARY
====================

Total Entries: 25

INFO: 8
WARNING: 7
ERROR: 8
DEBUG: 1
Malformed: 1

ERROR SUMMARY
-------------
Database connection failed: network timeout reaching db.internal: 4
File upload failed: permission denied for bucket application-logs: 2
Authentication failed: invalid token signature for user_502: 2

WARNING SUMMARY
---------------
Database response slow: 3
Memory usage high: 3
Cache miss ratio high: 1

Most Frequent Error:
Database connection failed: network timeout reaching db.internal

Most Frequent Warning:
Database response slow
```

---

## 17. Testing Instructions

Run the automated unittest suite:

```bash
python -m unittest discover -s tests
```

---

## 18. GitHub Setup

```bash
git init
git remote add origin https://github.com/your-username/log-analyzer.git
git add .
git commit -m "feat: complete Log Analyzer with Supabase Storage integration and RLS support"
git branch -M main
git push -u origin main
```

---

## 19. Troubleshooting

- **403 Unauthorized / RLS Violation**:
  - Solution 1: Use `SUPABASE_SERVICE_ROLE_KEY` in `.env`.
  - Solution 2: Run the SQL policies script in Supabase SQL Editor to grant permissions for `application-logs`.
- **Missing `.env`**: Ensure `.env` is created in root directory.

---

## 20. Security Notes
- Storage bucket `application-logs` is **private**.
- No credentials or API keys are committed to Git (`.env` is in `.gitignore`).
- RLS policies (if applied) are strictly scoped to `bucket_id = 'application-logs'`.
- The application fails loudly (`EXECUTION FAILED`) if a cloud upload/download operation fails.
