"""
Log Parser Module
Parses raw log strings/files into structured LogEntry instances.
"""
from dataclasses import dataclass
import re
from typing import List, Optional


@dataclass
class LogEntry:
    timestamp: Optional[str]
    level: str  # INFO, WARNING, ERROR, DEBUG, etc.
    message: str
    raw_line: str
    is_malformed: bool = False


LOG_PATTERN = re.compile(
    r"^(?P<timestamp>\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:?\d{2})?)?\s*"
    r"(?P<level>INFO|WARNING|WARN|ERROR|DEBUG|CRITICAL|FATAL)\s+"
    r"(?P<message>.+)$",
    re.IGNORECASE,
)


def parse_log_line(line: str) -> LogEntry:
    """
    Parses a single log line into a LogEntry object.
    Normalizes WARN to WARNING. Returns a malformed entry if parsing fails.
    """
    raw_line = line.strip()
    if not raw_line:
        return LogEntry(
            timestamp=None,
            level="MALFORMED",
            message="",
            raw_line=line,
            is_malformed=True,
        )

    match = LOG_PATTERN.match(raw_line)
    if not match:
        return LogEntry(
            timestamp=None,
            level="MALFORMED",
            message=raw_line,
            raw_line=raw_line,
            is_malformed=True,
        )

    timestamp = match.group("timestamp")
    level_raw = match.group("level").upper()
    message = match.group("message").strip()

    # Normalize WARN -> WARNING
    level = "WARNING" if level_raw == "WARN" else level_raw

    return LogEntry(
        timestamp=timestamp,
        level=level,
        message=message,
        raw_line=raw_line,
        is_malformed=False,
    )


def parse_log_content(content: str) -> List[LogEntry]:
    """
    Parses complete log file content into a list of LogEntry items.
    """
    lines = content.splitlines()
    entries = []
    for line in lines:
        if not line.strip():
            continue
        entries.append(parse_log_line(line))
    return entries


def parse_log_file(file_path: str) -> List[LogEntry]:
    """
    Reads a file from disk and parses its lines into LogEntry objects.
    """
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    return parse_log_content(content)
