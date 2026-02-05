"""T099: Tests for structured JSON logging configuration."""

import json
import logging

import pytest


class TestJSONFormatter:
    """Test JSONFormatter produces valid structured logs."""

    def test_basic_log_entry(self):
        from src.logging_config import JSONFormatter

        formatter = JSONFormatter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Test message",
            args=None,
            exc_info=None,
        )

        output = formatter.format(record)
        parsed = json.loads(output)

        assert parsed["level"] == "INFO"
        assert parsed["logger"] == "test"
        assert parsed["message"] == "Test message"
        assert "timestamp" in parsed

    def test_extra_fields_included(self):
        from src.logging_config import JSONFormatter

        formatter = JSONFormatter()
        record = logging.LogRecord(
            name="chat",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Chat request",
            args=None,
            exc_info=None,
        )
        record.user_id = "user-123"
        record.conversation_id = "conv-456"
        record.duration_ms = 1500

        output = formatter.format(record)
        parsed = json.loads(output)

        assert parsed["user_id"] == "user-123"
        assert parsed["conversation_id"] == "conv-456"
        assert parsed["duration_ms"] == 1500

    def test_exception_info_included(self):
        from src.logging_config import JSONFormatter

        formatter = JSONFormatter()

        try:
            raise ValueError("test error")
        except ValueError:
            import sys
            exc_info = sys.exc_info()

        record = logging.LogRecord(
            name="test",
            level=logging.ERROR,
            pathname="",
            lineno=0,
            msg="Error occurred",
            args=None,
            exc_info=exc_info,
        )

        output = formatter.format(record)
        parsed = json.loads(output)

        assert "exception" in parsed
        assert "ValueError" in parsed["exception"]


class TestConfigureLogging:
    """Test configure_logging function."""

    def test_configure_json_logging(self):
        from src.logging_config import configure_logging

        configure_logging(level="DEBUG", json_output=True)

        root = logging.getLogger()
        assert root.level == logging.DEBUG
        assert len(root.handlers) == 1

    def test_configure_text_logging(self):
        from src.logging_config import configure_logging

        configure_logging(level="WARNING", json_output=False)

        root = logging.getLogger()
        assert root.level == logging.WARNING
