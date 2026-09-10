"""
Report Generator Module
Generates JSON and TXT format summary reports from AnalysisResult.
"""
import json
import os
from typing import Tuple
from analyzer.log_analyzer import AnalysisResult


class ReportGenerator:
    """
    Handles serializing AnalysisResult into structured JSON and human-readable TXT files.
    """

    def __init__(self, result: AnalysisResult):
        self.result = result

    def generate_json(self, output_path: str) -> str:
        """
        Generates and saves JSON report to output_path. Returns JSON string content.
        """
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        data = self.result.to_dict()
        content = json.dumps(data, indent=2)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(content)
        return content

    def generate_txt(self, output_path: str) -> str:
        """
        Generates and saves TXT summary report to output_path. Returns TXT string content.
        """
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

        lines = [
            "LOG ANALYSIS SUMMARY",
            "====================",
            "",
            f"Total Entries: {self.result.total_entries}",
            "",
            f"INFO: {self.result.info_count}",
            f"WARNING: {self.result.warning_count}",
            f"ERROR: {self.result.error_count}",
            f"DEBUG: {self.result.debug_count}",
            f"Malformed: {self.result.malformed_count}",
            "",
            "ERROR SUMMARY",
            "-------------",
        ]

        if self.result.grouped_errors:
            for item in self.result.grouped_errors:
                lines.append(f"{item.message}: {item.count}")
        else:
            lines.append("No errors detected.")

        lines.extend(
            [
                "",
                "WARNING SUMMARY",
                "---------------",
            ]
        )

        if self.result.grouped_warnings:
            for item in self.result.grouped_warnings:
                lines.append(f"{item.message}: {item.count}")
        else:
            lines.append("No warnings detected.")

        lines.extend(
            [
                "",
                "Most Frequent Error:",
                self.result.most_frequent_error or "None",
                "",
                "Most Frequent Warning:",
                self.result.most_frequent_warning or "None",
                "",
            ]
        )

        content = "\n".join(lines)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(content)
        return content

    def generate_all(self, json_path: str, txt_path: str) -> Tuple[str, str]:
        """
        Generates both JSON and TXT summary reports.
        """
        json_content = self.generate_json(json_path)
        txt_content = self.generate_txt(txt_path)
        return json_content, txt_content
