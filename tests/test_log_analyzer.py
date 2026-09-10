"""
Unit Test Suite for Log Analyzer
Tests log parsing, log level counting, duplicate grouping, malformed line handling, and report generation.
"""
import json
import os
import tempfile
import unittest

from analyzer.log_analyzer import LogAnalyzer
from analyzer.log_parser import LogEntry, parse_log_content, parse_log_line
from analyzer.report_generator import ReportGenerator


class TestLogParser(unittest.TestCase):

    def test_parse_info_line(self):
        line = "2026-09-10 09:00:01 INFO Application started successfully"
        entry = parse_log_line(line)
        self.assertFalse(entry.is_malformed)
        self.assertEqual(entry.level, "INFO")
        self.assertEqual(entry.timestamp, "2026-09-10 09:00:01")
        self.assertEqual(entry.message, "Application started successfully")

    def test_parse_warning_line(self):
        line = "2026-09-10 09:01:03 WARNING Database response slow"
        entry = parse_log_line(line)
        self.assertFalse(entry.is_malformed)
        self.assertEqual(entry.level, "WARNING")
        self.assertEqual(entry.message, "Database response slow")

    def test_parse_warn_line_normalization(self):
        line = "2026-09-10 09:02:15 WARN Memory usage high"
        entry = parse_log_line(line)
        self.assertFalse(entry.is_malformed)
        self.assertEqual(entry.level, "WARNING")
        self.assertEqual(entry.message, "Memory usage high")

    def test_parse_error_line(self):
        line = "2026-09-10 09:01:15 ERROR Database connection failed"
        entry = parse_log_line(line)
        self.assertFalse(entry.is_malformed)
        self.assertEqual(entry.level, "ERROR")
        self.assertEqual(entry.message, "Database connection failed")

    def test_parse_malformed_line(self):
        line = "[INVALID LOG DATA WITHOUT LEVEL OR STAMP]"
        entry = parse_log_line(line)
        self.assertTrue(entry.is_malformed)
        self.assertEqual(entry.level, "MALFORMED")


class TestLogAnalyzer(unittest.TestCase):

    def setUp(self):
        self.sample_logs = """
2026-09-10 09:00:01 INFO System online
2026-09-10 09:00:15 INFO Database connected
2026-09-10 09:01:00 WARNING Disk usage high
2026-09-10 09:01:30 WARN Disk usage high
2026-09-10 09:02:00 ERROR Connection lost
2026-09-10 09:02:30 ERROR Connection lost
2026-09-10 09:03:00 ERROR Connection lost
2026-09-10 09:03:30 DEBUG Memory dump trace
INVALID RANDOM CORRUPTED LINE
"""
        self.entries = parse_log_content(self.sample_logs)
        self.analyzer = LogAnalyzer(self.entries)
        self.result = self.analyzer.analyze()

    def test_counting_log_levels(self):
        self.assertEqual(self.result.total_entries, 9)
        self.assertEqual(self.result.info_count, 2)
        self.assertEqual(self.result.warning_count, 2)
        self.assertEqual(self.result.error_count, 3)
        self.assertEqual(self.result.debug_count, 1)
        self.assertEqual(self.result.malformed_count, 1)

    def test_grouping_duplicate_errors(self):
        self.assertEqual(self.result.unique_errors, 1)
        self.assertEqual(self.result.most_frequent_error, "Connection lost")
        self.assertEqual(self.result.grouped_errors[0].count, 3)

    def test_grouping_duplicate_warnings(self):
        self.assertEqual(self.result.unique_warnings, 1)
        self.assertEqual(self.result.most_frequent_warning, "Disk usage high")
        self.assertEqual(self.result.grouped_warnings[0].count, 2)

    def test_handling_malformed_lines(self):
        self.assertEqual(self.result.malformed_count, 1)


class TestReportGenerator(unittest.TestCase):

    def test_generate_json_and_txt_summary(self):
        entries = parse_log_content("""
2026-09-10 09:00:00 INFO Started
2026-09-10 09:01:00 ERROR Timeout
2026-09-10 09:02:00 ERROR Timeout
2026-09-10 09:03:00 WARNING High Latency
""")
        analyzer = LogAnalyzer(entries)
        result = analyzer.analyze()
        generator = ReportGenerator(result)

        with tempfile.TemporaryDirectory() as tmpdir:
            json_path = os.path.join(tmpdir, "summary.json")
            txt_path = os.path.join(tmpdir, "summary.txt")

            generator.generate_all(json_path, txt_path)

            self.assertTrue(os.path.exists(json_path))
            self.assertTrue(os.path.exists(txt_path))

            with open(json_path, "r", encoding="utf-8") as f:
                json_data = json.load(f)
                self.assertEqual(json_data["analysis"]["total_entries"], 4)
                self.assertEqual(json_data["analysis"]["errors"], 2)
                self.assertEqual(json_data["most_frequent_error"], "Timeout")

            with open(txt_path, "r", encoding="utf-8") as f:
                txt_data = f.read()
                self.assertIn("LOG ANALYSIS SUMMARY", txt_data)
                self.assertIn("Total Entries: 4", txt_data)
                self.assertIn("ERROR: 2", txt_data)
                self.assertIn("Timeout: 2", txt_data)


if __name__ == "__main__":
    unittest.main()
