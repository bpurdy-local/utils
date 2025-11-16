import datetime
import json
import logging
import re
import threading
from pathlib import Path
from typing import Any

from utils.json_encoder import JsonEncoder


class Logger:
    """Static utility class for structured JSON logging with thread-local context."""

    _context_storage = threading.local()  # Thread-safe context storage
    _logger = None
    _configured = False

    @classmethod
    def _get_context(cls) -> dict[str, Any]:
        if not hasattr(cls._context_storage, "context"):
            cls._context_storage.context = {}
        return cls._context_storage.context

    @classmethod
    def _normalize_key(cls, key: str) -> str:
        # Convert keys to snake_case for consistent log field names
        # Handles: camelCase, PascalCase, kebab-case, spaces, consecutive caps
        key = re.sub(r"([a-z])([A-Z])", r"\1_\2", key)  # camelCase -> camel_Case
        key = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1_\2", key)  # HTTPServer -> HTTP_Server
        key = key.replace("-", "_").replace(" ", "_")  # kebab/spaces to underscores
        key = re.sub(r"_+", "_", key)  # Consolidate multiple underscores
        key = key.strip("_").lower()  # Trim and lowercase
        return key

    @classmethod
    def _ensure_configured(cls):
        if not cls._configured:
            cls._logger = logging.getLogger("utils.logger")
            if not cls._logger.handlers:
                handler = logging.StreamHandler()
                formatter = logging.Formatter("%(message)s")
                handler.setFormatter(formatter)
                cls._logger.addHandler(handler)
                cls._logger.setLevel(logging.INFO)
            cls._configured = True

    @staticmethod
    def bind(key: str, value: Any):
        """Bind a key-value pair to the thread-local logging context."""
        normalized_key = Logger._normalize_key(key)
        context = Logger._get_context()
        context[normalized_key] = value

    @staticmethod
    def bind_multiple(**kwargs):
        """Bind multiple key-value pairs to the logging context."""
        context = Logger._get_context()
        for key, value in kwargs.items():
            normalized_key = Logger._normalize_key(key)
            context[normalized_key] = value

    @staticmethod
    def unbind(key: str):
        """Remove a key from the logging context."""
        normalized_key = Logger._normalize_key(key)
        context = Logger._get_context()
        context.pop(normalized_key, None)

    @staticmethod
    def clear_context():
        """Clear all entries from the logging context."""
        context = Logger._get_context()
        context.clear()

    @staticmethod
    def get_context() -> dict[str, Any]:
        """Get a copy of the current logging context."""
        return Logger._get_context().copy()

    @classmethod
    def _parse_log_input(cls, *args, **kwargs) -> dict[str, Any]:
        if len(args) == 1 and isinstance(args[0], str) and not kwargs:
            return {"message": args[0]}
        elif len(args) == 1 and isinstance(args[0], dict) and not kwargs:
            normalized = {}
            for key, value in args[0].items():
                normalized_key = cls._normalize_key(key)
                normalized[normalized_key] = value
            return normalized
        elif not args and kwargs:
            normalized = {}
            for key, value in kwargs.items():
                normalized_key = cls._normalize_key(key)
                normalized[normalized_key] = value
            return normalized
        else:
            raise ValueError("Logger accepts either: a string, a dict, or keyword arguments")

    @classmethod
    def _format_log_entry(cls, level: str, log_data: dict[str, Any]) -> str:
        cls._ensure_configured()

        context = cls._get_context()
        entry = {}

        entry["timestamp"] = datetime.datetime.now(datetime.UTC).isoformat()
        entry["level"] = level

        entry.update(context)
        entry.update(log_data)

        # Ensure timestamp and level cannot be overridden by user data
        if "timestamp" in log_data:
            entry["timestamp"] = datetime.datetime.now(datetime.UTC).isoformat()
        if "level" in log_data:
            entry["level"] = level
        if "message" not in entry:
            entry["message"] = ""

        return json.dumps(entry, cls=JsonEncoder)

    @staticmethod
    def debug(*args, **kwargs):
        """Log message at DEBUG level."""
        log_data = Logger._parse_log_input(*args, **kwargs)
        formatted = Logger._format_log_entry("DEBUG", log_data)
        Logger._logger.debug(formatted)

    @staticmethod
    def info(*args, **kwargs):
        """Log message at INFO level."""
        log_data = Logger._parse_log_input(*args, **kwargs)
        formatted = Logger._format_log_entry("INFO", log_data)
        Logger._logger.info(formatted)

    @staticmethod
    def warning(*args, **kwargs):
        """Log message at WARNING level."""
        log_data = Logger._parse_log_input(*args, **kwargs)
        formatted = Logger._format_log_entry("WARNING", log_data)
        Logger._logger.warning(formatted)

    @staticmethod
    def error(*args, **kwargs):
        """Log message at ERROR level."""
        log_data = Logger._parse_log_input(*args, **kwargs)
        formatted = Logger._format_log_entry("ERROR", log_data)
        Logger._logger.error(formatted)

    @staticmethod
    def critical(*args, **kwargs):
        """Log message at CRITICAL level."""
        log_data = Logger._parse_log_input(*args, **kwargs)
        formatted = Logger._format_log_entry("CRITICAL", log_data)
        Logger._logger.critical(formatted)

    @staticmethod
    def context(**kwargs):
        """Create a context manager for temporary logging context."""
        return LoggerContext(kwargs)

    @staticmethod
    def search(
        log_file: str,
        *,
        level: str | None = None,
        start_time: str | None = None,
        end_time: str | None = None,
        message_contains: str | None = None,
        message_pattern: str | None = None,
        context: dict[str, Any] | None = None,
        has_keys: list[str] | None = None,
        missing_keys: list[str] | None = None,
    ) -> list[dict[str, Any]]:
        """Search log file for entries matching specified criteria."""
        log_path = Path(log_file)
        if not log_path.exists():
            raise FileNotFoundError(f"Log file not found: {log_file}")

        results = []
        pattern = re.compile(message_pattern) if message_pattern else None

        with open(log_path) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue

                try:
                    entry = json.loads(line)
                except json.JSONDecodeError:
                    continue

                if level and entry.get("level") != level:
                    continue

                if start_time and entry.get("timestamp", "") < start_time:
                    continue

                if end_time and entry.get("timestamp", "") >= end_time:
                    continue

                if message_contains and message_contains not in entry.get("message", ""):
                    continue

                if pattern and not pattern.search(entry.get("message", "")):
                    continue

                if context:
                    match = True
                    for key, value in context.items():
                        if entry.get(key) != value:
                            match = False
                            break
                    if not match:
                        continue

                if has_keys and not all(key in entry for key in has_keys):
                    continue

                if missing_keys and any(key in entry for key in missing_keys):
                    continue

                results.append(entry)

        return results


class LoggerContext:
    def __init__(self, context_data: dict[str, Any]):
        self.context_data = context_data
        self.saved_keys = set()

    def __enter__(self):
        for key, value in self.context_data.items():
            normalized_key = Logger._normalize_key(key)
            context = Logger._get_context()
            if normalized_key in context:
                self.saved_keys.add(normalized_key)
            else:
                self.saved_keys.add(normalized_key)
            Logger.bind(key, value)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        for key in self.saved_keys:
            Logger.unbind(key)
