"""
Log Analyzer Module
Aggregates and summarizes log metrics from parsed log entries.
"""
from collections import Counter
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from analyzer.log_parser import LogEntry


@dataclass
class GroupedMessage:
    message: str
    count: int


@dataclass
class AnalysisResult:
    total_entries: int
    info_count: int
    warning_count: int
    error_count: int
    debug_count: int
    malformed_count: int
    unique_errors: int
    unique_warnings: int
    most_frequent_error: Optional[str]
    most_frequent_warning: Optional[str]
    error_percentage: float
    warning_percentage: float
    grouped_errors: List[GroupedMessage] = field(default_factory=list)
    grouped_warnings: List[GroupedMessage] = field(default_factory=list)

    def to_dict(self) -> dict:
        """
        Converts analysis result to structured dictionary matching report specification.
        """
        return {
            "analysis": {
                "total_entries": self.total_entries,
                "info": self.info_count,
                "warnings": self.warning_count,
                "errors": self.error_count,
                "debug": self.debug_count,
                "malformed": self.malformed_count,
                "unique_errors": self.unique_errors,
                "unique_warnings": self.unique_warnings,
                "error_percentage": round(self.error_percentage, 2),
                "warning_percentage": round(self.warning_percentage, 2),
            },
            "errors": [
                {"message": item.message, "count": item.count}
                for item in self.grouped_errors
            ],
            "warnings": [
                {"message": item.message, "count": item.count}
                for item in self.grouped_warnings
            ],
            "most_frequent_error": self.most_frequent_error or "N/A",
            "most_frequent_warning": self.most_frequent_warning or "N/A",
        }


class LogAnalyzer:
    """
    Analyzes a list of LogEntry objects and calculates dynamic log statistics.
    """

    def __init__(self, entries: List[LogEntry]):
        self.entries = entries

    def analyze(self) -> AnalysisResult:
        """
        Executes log metrics analysis and returns AnalysisResult.
        """
        total_entries = len(self.entries)

        info_count = 0
        warning_count = 0
        error_count = 0
        debug_count = 0
        malformed_count = 0

        error_messages: List[str] = []
        warning_messages: List[str] = []

        for entry in self.entries:
            if entry.is_malformed:
                malformed_count += 1
                continue

            lvl = entry.level
            if lvl == "INFO":
                info_count += 1
            elif lvl == "WARNING":
                warning_count += 1
                warning_messages.append(entry.message)
            elif lvl == "ERROR":
                error_count += 1
                error_messages.append(entry.message)
            elif lvl == "DEBUG":
                debug_count += 1
            else:
                info_count += 1

        error_counter = Counter(error_messages)
        warning_counter = Counter(warning_messages)

        grouped_errors = [
            GroupedMessage(message=msg, count=count)
            for msg, count in error_counter.most_common()
        ]
        grouped_warnings = [
            GroupedMessage(message=msg, count=count)
            for msg, count in warning_counter.most_common()
        ]

        most_frequent_error = (
            grouped_errors[0].message if grouped_errors else None
        )
        most_frequent_warning = (
            grouped_warnings[0].message if grouped_warnings else None
        )

        error_pct = (
            (error_count / total_entries * 100.0) if total_entries > 0 else 0.0
        )
        warning_pct = (
            (warning_count / total_entries * 100.0) if total_entries > 0 else 0.0
        )

        return AnalysisResult(
            total_entries=total_entries,
            info_count=info_count,
            warning_count=warning_count,
            error_count=error_count,
            debug_count=debug_count,
            malformed_count=malformed_count,
            unique_errors=len(grouped_errors),
            unique_warnings=len(grouped_warnings),
            most_frequent_error=most_frequent_error,
            most_frequent_warning=most_frequent_warning,
            error_percentage=error_pct,
            warning_percentage=warning_pct,
            grouped_errors=grouped_errors,
            grouped_warnings=grouped_warnings,
        )
