"""
Log Analyzer CLI Application
Orchestrates uploading log files to Supabase Storage, downloading and parsing logs,
generating metrics and reports, uploading reports back to cloud storage, and printing summary statistics.
"""
import os
import sys
from dotenv import load_dotenv

from analyzer.log_analyzer import LogAnalyzer
from analyzer.log_parser import parse_log_content
from analyzer.report_generator import ReportGenerator
from analyzer.supabase_storage import SupabaseStorageManager

LOCAL_LOG_PATH = os.path.join("logs", "application.log")
LOCAL_JSON_PATH = os.path.join("reports", "summary.json")
LOCAL_TXT_PATH = os.path.join("reports", "summary.txt")

REMOTE_LOG_PATH = "logs/application.log"
REMOTE_JSON_PATH = "reports/summary.json"
REMOTE_TXT_PATH = "reports/summary.txt"


def print_banner():
    print("========================================")
    print("       LOG ANALYZER PROCESS APP         ")
    print("========================================")
    print()


def run():
    load_dotenv()
    print_banner()

    # Step 1: Verify local input log file existence
    if not os.path.exists(LOCAL_LOG_PATH):
        print(f"[ERROR] Sample log file not found at: {LOCAL_LOG_PATH}")
        print("Please ensure logs/application.log exists before running.")
        sys.exit(1)

    storage = SupabaseStorageManager()

    # Check if credentials are set
    has_credentials = bool(
        storage.supabase_url
        and storage.supabase_url != "https://your-project-id.supabase.co"
        and storage.supabase_key
        and storage.supabase_key
        not in (
            "your-supabase-api-key-here",
            "your-supabase-service-role-key-here",
        )
    )

    cloud_attempted = False
    cloud_failed = False

    conn_status = "SKIPPED"
    upload_log_status = "SKIPPED"
    download_log_status = "SKIPPED"
    analysis_status = "PENDING"
    report_gen_status = "PENDING"
    upload_reports_status = "SKIPPED"

    # Step 2: Connect to Supabase Storage if configured
    print("Connecting to Supabase...")
    if has_credentials:
        cloud_attempted = True
        try:
            storage.connect()
            storage.ensure_bucket_exists()
            conn_status = "SUCCESS"
            print("Connected successfully to Supabase Storage.")
        except Exception as e:
            conn_status = f"FAILED ({e})"
            cloud_failed = True
            print(f"[ERROR] Connection to Supabase failed: {e}")
    else:
        print("[NOTICE] No Supabase credentials configured in .env.")
        print(
            "Running in local analysis mode. Set SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY (or SUPABASE_KEY) in .env to enable Cloud Storage."
        )
        print()

    log_content = ""

    # Step 3: Cloud Upload & Download (if cloud configured and connection succeeded)
    if cloud_attempted and not cloud_failed:
        # Upload Log File
        print(
            f"\nUploading '{LOCAL_LOG_PATH}' to Supabase Storage path '{REMOTE_LOG_PATH}'..."
        )
        try:
            storage.upload_file(LOCAL_LOG_PATH, REMOTE_LOG_PATH)
            upload_log_status = "SUCCESS"
            print("Upload successful.")
        except Exception as e:
            upload_log_status = f"FAILED ({e})"
            cloud_failed = True
            print(f"[ERROR] Log upload failed: {e}")

        # Download Log File
        if not cloud_failed:
            print(
                f"\nDownloading log file from Supabase Storage path '{REMOTE_LOG_PATH}'..."
            )
            try:
                log_content = storage.download_as_text(REMOTE_LOG_PATH)
                download_log_status = "SUCCESS"
                print("Download successful.")
            except Exception as e:
                download_log_status = f"FAILED ({e})"
                cloud_failed = True
                print(f"[ERROR] Log download failed: {e}")

    # Fallback to local log file if cloud was not configured
    if not cloud_attempted:
        with open(LOCAL_LOG_PATH, "r", encoding="utf-8") as f:
            log_content = f.read()

    # If cloud attempted and failed, print status breakdown & exit with failure
    if cloud_attempted and cloud_failed:
        print("\n========================================")
        print("       EXECUTION STATUS BREAKDOWN       ")
        print("========================================")
        print(f"Supabase Connection : {conn_status}")
        print(f"Log Upload          : {upload_log_status}")
        print(f"Log Download        : {download_log_status}")
        print("========================================")
        print("        EXECUTION FAILED                ")
        print("========================================")
        print(
            "\nCloud storage operation failed. Please verify credentials or RLS policies."
        )
        sys.exit(1)

    # Step 4: Process & Parse Logs
    print("\nProcessing logs...")
    try:
        entries = parse_log_content(log_content)
        analyzer = LogAnalyzer(entries)
        result = analyzer.analyze()
        analysis_status = "SUCCESS"
    except Exception as e:
        analysis_status = f"FAILED ({e})"
        print(f"[ERROR] Log parsing and analysis failed: {e}")
        sys.exit(1)

    print("\nAnalysis completed.")
    print("----------------------------------------")
    print(f"Total Logs : {result.total_entries}")
    print(f"Errors     : {result.error_count} ({result.error_percentage:.1f}%)")
    print(
        f"Warnings   : {result.warning_count} ({result.warning_percentage:.1f}%)"
    )
    print(f"Info       : {result.info_count}")
    print(f"Debug      : {result.debug_count}")
    print(f"Malformed  : {result.malformed_count}")
    print("----------------------------------------")
    if result.most_frequent_error:
        print(f"Most Frequent Error   : {result.most_frequent_error}")
    if result.most_frequent_warning:
        print(f"Most Frequent Warning : {result.most_frequent_warning}")
    print("----------------------------------------")

    # Step 5: Report Generation
    print("\nGenerating reports...")
    try:
        report_gen = ReportGenerator(result)
        report_gen.generate_all(LOCAL_JSON_PATH, LOCAL_TXT_PATH)
        report_gen_status = "SUCCESS"
        print(f"[OK] {LOCAL_JSON_PATH} created")
        print(f"[OK] {LOCAL_TXT_PATH} created")
    except Exception as e:
        report_gen_status = f"FAILED ({e})"
        print(f"[ERROR] Report generation failed: {e}")
        sys.exit(1)

    # Step 6: Upload Reports to Supabase Storage
    if cloud_attempted and not cloud_failed:
        print("\nUploading reports to Supabase Storage...")
        try:
            storage.upload_file(LOCAL_JSON_PATH, REMOTE_JSON_PATH)
            print(f"[OK] {REMOTE_JSON_PATH} uploaded successfully.")
            storage.upload_file(LOCAL_TXT_PATH, REMOTE_TXT_PATH)
            print(f"[OK] {REMOTE_TXT_PATH} uploaded successfully.")
            upload_reports_status = "SUCCESS"
            print("Reports uploaded successfully to Supabase Storage.")
        except Exception as e:
            upload_reports_status = f"FAILED ({e})"
            cloud_failed = True
            print(f"[ERROR] Uploading reports to Supabase failed: {e}")
            print("\n========================================")
            print("       EXECUTION STATUS BREAKDOWN       ")
            print("========================================")
            print(f"Supabase Connection : {conn_status}")
            print(f"Log Upload          : {upload_log_status}")
            print(f"Log Download        : {download_log_status}")
            print(f"Log Analysis        : {analysis_status}")
            print(f"Report Generation   : {report_gen_status}")
            print(f"Report Upload       : {upload_reports_status}")
            print("========================================")
            print("        EXECUTION FAILED                ")
            print("========================================")
            sys.exit(1)

    # Step 7: Final Execution Status Output
    print("\n========================================")
    print("       EXECUTION STATUS BREAKDOWN       ")
    print("========================================")
    if cloud_attempted:
        print(f"Supabase Connection : {conn_status}")
        print(f"Log Upload          : {upload_log_status}")
        print(f"Log Download        : {download_log_status}")
    print(f"Log Analysis        : {analysis_status}")
    print(f"Report Generation   : {report_gen_status}")
    if cloud_attempted:
        print(f"Report Upload       : {upload_reports_status}")

    print("========================================")
    if cloud_attempted and not cloud_failed:
        print("        EXECUTION COMPLETED             ")
    else:
        print("  LOCAL DEMONSTRATION COMPLETED        ")
    print("========================================")


if __name__ == "__main__":
    run()
