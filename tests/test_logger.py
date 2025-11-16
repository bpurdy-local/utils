import datetime
import json
import logging
import tempfile
import threading
from pathlib import Path

import pytest

from utils.logger import Logger


@pytest.fixture(autouse=True)
def reset_logger():
    Logger.clear_context()
    Logger._configured = False
    Logger._logger = None
    Logger._ensure_configured()
    Logger._logger.setLevel(logging.DEBUG)
    yield
    Logger.clear_context()


def test_basic_info_logging(caplog):
    with caplog.at_level(logging.INFO):
        Logger.info("Test message")
    assert len(caplog.records) == 1
    log_data = json.loads(caplog.records[0].message)
    assert log_data["level"] == "INFO"
    assert log_data["message"] == "Test message"
    assert "timestamp" in log_data


def test_all_log_levels(caplog):
    with caplog.at_level(logging.DEBUG):
        Logger.debug("Debug message")
        Logger.info("Info message")
        Logger.warning("Warning message")
        Logger.error("Error message")
        Logger.critical("Critical message")

    assert len(caplog.records) == 5
    levels = [json.loads(r.message)["level"] for r in caplog.records]
    assert levels == ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]


def test_string_input_format(caplog):
    with caplog.at_level(logging.INFO):
        Logger.info("Simple message")
    log_data = json.loads(caplog.records[0].message)
    assert log_data["message"] == "Simple message"


def test_dict_input_format(caplog):
    with caplog.at_level(logging.INFO):
        Logger.info({"message": "Test", "userId": "123", "action": "login"})
    log_data = json.loads(caplog.records[0].message)
    assert log_data["message"] == "Test"
    assert log_data["user_id"] == "123"
    assert log_data["action"] == "login"


def test_kwargs_input_format(caplog):
    with caplog.at_level(logging.INFO):
        Logger.info(message="Test", userId="123", action="login")
    log_data = json.loads(caplog.records[0].message)
    assert log_data["message"] == "Test"
    assert log_data["user_id"] == "123"
    assert log_data["action"] == "login"


def test_all_three_formats_produce_identical_output(caplog):
    with caplog.at_level(logging.INFO):
        Logger.clear_context()
        Logger.info({"message": "Test", "user_id": "123"})
        dict_output = json.loads(caplog.records[0].message)

        caplog.clear()
        Logger.clear_context()
        Logger.info(message="Test", user_id="123")
        kwargs_output = json.loads(caplog.records[0].message)

    dict_output.pop("timestamp")
    kwargs_output.pop("timestamp")
    assert dict_output == kwargs_output


def test_key_normalization_camel_case(caplog):
    with caplog.at_level(logging.INFO):
        Logger.info({"userId": "123", "requestId": "abc"})
    log_data = json.loads(caplog.records[0].message)
    assert "user_id" in log_data
    assert "request_id" in log_data


def test_key_normalization_pascal_case(caplog):
    with caplog.at_level(logging.INFO):
        Logger.info({"UserID": "123", "RequestID": "abc"})
    log_data = json.loads(caplog.records[0].message)
    assert "user_id" in log_data
    assert "request_id" in log_data


def test_key_normalization_kebab_case(caplog):
    with caplog.at_level(logging.INFO):
        Logger.info({"user-id": "123", "request-id": "abc"})
    log_data = json.loads(caplog.records[0].message)
    assert "user_id" in log_data
    assert "request_id" in log_data


def test_key_normalization_spaces(caplog):
    with caplog.at_level(logging.INFO):
        Logger.info({"user id": "123", "request id": "abc"})
    log_data = json.loads(caplog.records[0].message)
    assert "user_id" in log_data
    assert "request_id" in log_data


def test_key_normalization_removes_leading_trailing_underscores():
    Logger.bind("__key__", "value")
    context = Logger.get_context()
    assert "key" in context


def test_key_normalization_collapses_separators():
    Logger.bind("my___weird__key", "value")
    context = Logger.get_context()
    assert "my_weird_key" in context


def test_reserved_keys_protected(caplog):
    with caplog.at_level(logging.INFO):
        Logger.info({"timestamp": "wrong", "level": "WRONG", "message": "Correct"})
    log_data = json.loads(caplog.records[0].message)
    assert log_data["level"] == "INFO"
    assert log_data["message"] == "Correct"
    assert log_data["timestamp"] != "wrong"


def test_bind_single_key():
    Logger.bind("requestId", "12345")
    context = Logger.get_context()
    assert context["request_id"] == "12345"


def test_bind_multiple_keys():
    Logger.bind_multiple(requestId="123", userId="456", sessionId="789")
    context = Logger.get_context()
    assert context["request_id"] == "123"
    assert context["user_id"] == "456"
    assert context["session_id"] == "789"


def test_unbind_key():
    Logger.bind("key1", "value1")
    Logger.bind("key2", "value2")
    Logger.unbind("key1")
    context = Logger.get_context()
    assert "key1" not in context
    assert "key2" in context


def test_clear_context():
    Logger.bind_multiple(key1="value1", key2="value2", key3="value3")
    Logger.clear_context()
    context = Logger.get_context()
    assert len(context) == 0


def test_get_context():
    Logger.bind("key", "value")
    context = Logger.get_context()
    assert context == {"key": "value"}
    context["key"] = "modified"
    original = Logger.get_context()
    assert original["key"] == "value"


def test_context_persistence(caplog):
    Logger.bind("request_id", "abc123")
    with caplog.at_level(logging.INFO):
        Logger.info("First message")
        Logger.info("Second message")
    assert len(caplog.records) == 2
    log1 = json.loads(caplog.records[0].message)
    log2 = json.loads(caplog.records[1].message)
    assert log1["request_id"] == "abc123"
    assert log2["request_id"] == "abc123"


def test_inline_fields_merge_with_context(caplog):
    Logger.bind("request_id", "abc123")
    with caplog.at_level(logging.INFO):
        Logger.info(message="Test", user_id="user456")
    log_data = json.loads(caplog.records[0].message)
    assert log_data["request_id"] == "abc123"
    assert log_data["user_id"] == "user456"


def test_inline_fields_override_context(caplog):
    Logger.bind("user_id", "original")
    with caplog.at_level(logging.INFO):
        Logger.info(message="Test", user_id="override")
    log_data = json.loads(caplog.records[0].message)
    assert log_data["user_id"] == "override"


def test_thread_safety():
    results = {}

    def thread_func(thread_id):
        Logger.clear_context()
        Logger.bind("thread_id", thread_id)
        context = Logger.get_context()
        results[thread_id] = context["thread_id"]

    threads = [threading.Thread(target=thread_func, args=(i,)) for i in range(5)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    for i in range(5):
        assert results[i] == i


def test_context_manager(caplog):
    Logger.bind("persistent", "value1")
    with caplog.at_level(logging.INFO):
        with Logger.context(temporary="value2"):
            Logger.info("Inside context")
        Logger.info("Outside context")

    log1 = json.loads(caplog.records[0].message)
    log2 = json.loads(caplog.records[1].message)
    assert log1["persistent"] == "value1"
    assert log1["temporary"] == "value2"
    assert log2["persistent"] == "value1"
    assert "temporary" not in log2


def test_nested_context_managers(caplog):
    with caplog.at_level(logging.INFO), Logger.context(level1="a"), Logger.context(level2="b"):
        Logger.info("Nested")

    log_data = json.loads(caplog.records[0].message)
    assert log_data["level1"] == "a"
    assert log_data["level2"] == "b"


def test_json_output_format(caplog):
    with caplog.at_level(logging.INFO):
        Logger.info("Test")
    message = caplog.records[0].message
    log_data = json.loads(message)
    assert "timestamp" in log_data
    assert "level" in log_data
    assert "message" in log_data


def test_tuple_in_log_data(caplog):
    with caplog.at_level(logging.INFO):
        Logger.info(message="Test", position=(10, 20, 30))
    log_data = json.loads(caplog.records[0].message)
    assert log_data["position"] == [10, 20, 30]


def test_set_in_log_data(caplog):
    with caplog.at_level(logging.INFO):
        Logger.info(message="Test", tags={"python", "logging"})
    log_data = json.loads(caplog.records[0].message)
    assert set(log_data["tags"]) == {"python", "logging"}


def test_datetime_in_log_data(caplog):
    with caplog.at_level(logging.INFO):
        dt = datetime.datetime(2025, 11, 15, 10, 30, 0)
        Logger.info(message="Test", event_time=dt)
    log_data = json.loads(caplog.records[0].message)
    assert log_data["event_time"] == "2025-11-15T10:30:00"


def test_custom_object_in_log_data(caplog):
    class User:
        def to_dict(self):
            return {"id": 123, "name": "Alice"}

    with caplog.at_level(logging.INFO):
        Logger.info(message="Test", user=User())
    log_data = json.loads(caplog.records[0].message)
    assert log_data["user"] == {"id": 123, "name": "Alice"}


def test_logger_output_is_valid_json(caplog):
    with caplog.at_level(logging.INFO):
        Logger.info(message="Test", position=(1, 2), tags={"a", "b"})
    message = caplog.records[0].message
    parsed = json.loads(message)
    assert isinstance(parsed, dict)


def test_none_values_in_context(caplog):
    with caplog.at_level(logging.INFO):
        Logger.info(message="Test", value=None)
    log_data = json.loads(caplog.records[0].message)
    assert log_data["value"] is None


def test_search_all_entries():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".log", delete=False) as f:
        f.write('{"timestamp": "2025-11-15T10:00:00", "level": "INFO", "message": "Test 1"}\n')
        f.write('{"timestamp": "2025-11-15T10:01:00", "level": "ERROR", "message": "Test 2"}\n')
        f.write('{"timestamp": "2025-11-15T10:02:00", "level": "INFO", "message": "Test 3"}\n')
        log_file = f.name

    try:
        results = Logger.search(log_file=log_file)
        assert len(results) == 3
    finally:
        Path(log_file).unlink()


def test_search_by_level():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".log", delete=False) as f:
        f.write('{"timestamp": "2025-11-15T10:00:00", "level": "INFO", "message": "Test 1"}\n')
        f.write('{"timestamp": "2025-11-15T10:01:00", "level": "ERROR", "message": "Test 2"}\n')
        f.write('{"timestamp": "2025-11-15T10:02:00", "level": "ERROR", "message": "Test 3"}\n')
        log_file = f.name

    try:
        results = Logger.search(log_file=log_file, level="ERROR")
        assert len(results) == 2
        assert all(r["level"] == "ERROR" for r in results)
    finally:
        Path(log_file).unlink()


def test_search_by_time_range():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".log", delete=False) as f:
        f.write('{"timestamp": "2025-11-15T09:00:00", "level": "INFO", "message": "Before"}\n')
        f.write('{"timestamp": "2025-11-15T10:00:00", "level": "INFO", "message": "During 1"}\n')
        f.write('{"timestamp": "2025-11-15T10:30:00", "level": "INFO", "message": "During 2"}\n')
        f.write('{"timestamp": "2025-11-15T11:00:00", "level": "INFO", "message": "After"}\n')
        log_file = f.name

    try:
        results = Logger.search(
            log_file=log_file, start_time="2025-11-15T10:00:00", end_time="2025-11-15T11:00:00"
        )
        assert len(results) == 2
        assert results[0]["message"] == "During 1"
        assert results[1]["message"] == "During 2"
    finally:
        Path(log_file).unlink()


def test_search_by_message_contains():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".log", delete=False) as f:
        f.write('{"timestamp": "2025-11-15T10:00:00", "level": "INFO", "message": "User login"}\n')
        f.write('{"timestamp": "2025-11-15T10:01:00", "level": "INFO", "message": "Data fetch"}\n')
        f.write('{"timestamp": "2025-11-15T10:02:00", "level": "INFO", "message": "User logout"}\n')
        log_file = f.name

    try:
        results = Logger.search(log_file=log_file, message_contains="User")
        assert len(results) == 2
        assert "User" in results[0]["message"]
        assert "User" in results[1]["message"]
    finally:
        Path(log_file).unlink()


def test_search_by_message_pattern():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".log", delete=False) as f:
        f.write('{"timestamp": "2025-11-15T10:00:00", "level": "INFO", "message": "user_123"}\n')
        f.write('{"timestamp": "2025-11-15T10:01:00", "level": "INFO", "message": "user_abc"}\n')
        f.write('{"timestamp": "2025-11-15T10:02:00", "level": "INFO", "message": "user_456"}\n')
        log_file = f.name

    try:
        results = Logger.search(log_file=log_file, message_pattern=r"user_\d+")
        assert len(results) == 2
        assert results[0]["message"] == "user_123"
        assert results[1]["message"] == "user_456"
    finally:
        Path(log_file).unlink()


def test_search_by_context():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".log", delete=False) as f:
        f.write(
            '{"timestamp": "2025-11-15T10:00:00", "level": "INFO", "message": "Test", "user_id": "123"}\n'
        )
        f.write(
            '{"timestamp": "2025-11-15T10:01:00", "level": "INFO", "message": "Test", "user_id": "456"}\n'
        )
        f.write(
            '{"timestamp": "2025-11-15T10:02:00", "level": "INFO", "message": "Test", "user_id": "123"}\n'
        )
        log_file = f.name

    try:
        results = Logger.search(log_file=log_file, context={"user_id": "123"})
        assert len(results) == 2
        assert all(r["user_id"] == "123" for r in results)
    finally:
        Path(log_file).unlink()


def test_search_with_combined_filters():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".log", delete=False) as f:
        f.write(
            '{"timestamp": "2025-11-15T10:00:00", "level": "ERROR", "message": "Auth failed", "request_id": "abc"}\n'
        )
        f.write(
            '{"timestamp": "2025-11-15T10:01:00", "level": "INFO", "message": "Auth failed", "request_id": "abc"}\n'
        )
        f.write(
            '{"timestamp": "2025-11-15T10:02:00", "level": "ERROR", "message": "Auth failed", "request_id": "xyz"}\n'
        )
        f.write(
            '{"timestamp": "2025-11-15T10:03:00", "level": "ERROR", "message": "Other error", "request_id": "abc"}\n'
        )
        log_file = f.name

    try:
        results = Logger.search(
            log_file=log_file, level="ERROR", message_contains="Auth", context={"request_id": "abc"}
        )
        assert len(results) == 1
        assert results[0]["message"] == "Auth failed"
        assert results[0]["level"] == "ERROR"
        assert results[0]["request_id"] == "abc"
    finally:
        Path(log_file).unlink()


def test_search_nonexistent_file():
    with pytest.raises(FileNotFoundError):
        Logger.search(log_file="/nonexistent/file.log")


def test_search_handles_malformed_json():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".log", delete=False) as f:
        f.write('{"timestamp": "2025-11-15T10:00:00", "level": "INFO", "message": "Good"}\n')
        f.write("This is not JSON\n")
        f.write('{"timestamp": "2025-11-15T10:01:00", "level": "INFO", "message": "Also good"}\n')
        log_file = f.name

    try:
        results = Logger.search(log_file=log_file)
        assert len(results) == 2
        assert results[0]["message"] == "Good"
        assert results[1]["message"] == "Also good"
    finally:
        Path(log_file).unlink()


def test_search_empty_file():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".log", delete=False) as f:
        log_file = f.name

    try:
        results = Logger.search(log_file=log_file)
        assert len(results) == 0
    finally:
        Path(log_file).unlink()


def test_search_returns_structured_data():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".log", delete=False) as f:
        f.write(
            '{"timestamp": "2025-11-15T10:00:00", "level": "INFO", "message": "Test", "extra": "data"}\n'
        )
        log_file = f.name

    try:
        results = Logger.search(log_file=log_file)
        assert len(results) == 1
        assert isinstance(results[0], dict)
        assert results[0]["timestamp"] == "2025-11-15T10:00:00"
        assert results[0]["level"] == "INFO"
        assert results[0]["message"] == "Test"
        assert results[0]["extra"] == "data"
    finally:
        Path(log_file).unlink()


def test_search_by_has_keys():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".log", delete=False) as f:
        f.write(
            '{"timestamp": "2025-11-15T10:00:00", "level": "INFO", "message": "Test", "user_id": "123", "request_id": "abc"}\n'
        )
        f.write(
            '{"timestamp": "2025-11-15T10:01:00", "level": "INFO", "message": "Test", "user_id": "456"}\n'
        )
        f.write(
            '{"timestamp": "2025-11-15T10:02:00", "level": "INFO", "message": "Test", "request_id": "xyz"}\n'
        )
        f.write('{"timestamp": "2025-11-15T10:03:00", "level": "INFO", "message": "Test"}\n')
        log_file = f.name

    try:
        # Find logs that have user_id key
        results = Logger.search(log_file=log_file, has_keys=["user_id"])
        assert len(results) == 2
        assert all("user_id" in r for r in results)

        # Find logs that have both user_id and request_id keys
        results = Logger.search(log_file=log_file, has_keys=["user_id", "request_id"])
        assert len(results) == 1
        assert results[0]["user_id"] == "123"
        assert results[0]["request_id"] == "abc"

        # Find logs that have request_id key
        results = Logger.search(log_file=log_file, has_keys=["request_id"])
        assert len(results) == 2
        assert all("request_id" in r for r in results)
    finally:
        Path(log_file).unlink()


def test_search_by_missing_keys():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".log", delete=False) as f:
        f.write(
            '{"timestamp": "2025-11-15T10:00:00", "level": "INFO", "message": "Test", "user_id": "123", "request_id": "abc"}\n'
        )
        f.write(
            '{"timestamp": "2025-11-15T10:01:00", "level": "INFO", "message": "Test", "user_id": "456"}\n'
        )
        f.write(
            '{"timestamp": "2025-11-15T10:02:00", "level": "INFO", "message": "Test", "request_id": "xyz"}\n'
        )
        f.write('{"timestamp": "2025-11-15T10:03:00", "level": "INFO", "message": "Test"}\n')
        log_file = f.name

    try:
        # Find logs that don't have user_id key
        results = Logger.search(log_file=log_file, missing_keys=["user_id"])
        assert len(results) == 2
        assert all("user_id" not in r for r in results)

        # Find logs that don't have both user_id and request_id keys
        results = Logger.search(log_file=log_file, missing_keys=["user_id", "request_id"])
        assert len(results) == 1
        assert "user_id" not in results[0]
        assert "request_id" not in results[0]
        assert results[0]["message"] == "Test"

        # Find logs that don't have request_id key
        results = Logger.search(log_file=log_file, missing_keys=["request_id"])
        assert len(results) == 2
        assert all("request_id" not in r for r in results)
    finally:
        Path(log_file).unlink()


def test_search_has_keys_and_missing_keys_combined():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".log", delete=False) as f:
        f.write(
            '{"timestamp": "2025-11-15T10:00:00", "level": "INFO", "message": "Test", "user_id": "123", "request_id": "abc"}\n'
        )
        f.write(
            '{"timestamp": "2025-11-15T10:01:00", "level": "INFO", "message": "Test", "user_id": "456"}\n'
        )
        f.write(
            '{"timestamp": "2025-11-15T10:02:00", "level": "INFO", "message": "Test", "session_id": "sess1"}\n'
        )
        f.write('{"timestamp": "2025-11-15T10:03:00", "level": "INFO", "message": "Test"}\n')
        log_file = f.name

    try:
        # Find logs that have user_id but don't have request_id
        results = Logger.search(
            log_file=log_file, has_keys=["user_id"], missing_keys=["request_id"]
        )
        assert len(results) == 1
        assert results[0]["user_id"] == "456"
        assert "request_id" not in results[0]

        # Find logs that have message but don't have user_id or session_id
        results = Logger.search(
            log_file=log_file, has_keys=["message"], missing_keys=["user_id", "session_id"]
        )
        assert len(results) == 1
        assert results[0]["message"] == "Test"
        assert "user_id" not in results[0]
        assert "session_id" not in results[0]
    finally:
        Path(log_file).unlink()


def test_search_with_all_filters_including_keys():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".log", delete=False) as f:
        f.write(
            '{"timestamp": "2025-11-15T10:00:00", "level": "ERROR", "message": "Auth failed", "user_id": "123", "request_id": "abc"}\n'
        )
        f.write(
            '{"timestamp": "2025-11-15T10:01:00", "level": "ERROR", "message": "Auth failed", "user_id": "456", "session_id": "sess1"}\n'
        )
        f.write(
            '{"timestamp": "2025-11-15T10:02:00", "level": "ERROR", "message": "Auth failed", "request_id": "xyz"}\n'
        )
        f.write(
            '{"timestamp": "2025-11-15T10:03:00", "level": "INFO", "message": "Auth failed", "user_id": "789", "request_id": "def"}\n'
        )
        log_file = f.name

    try:
        # Combine level, message, has_keys, and missing_keys filters
        results = Logger.search(
            log_file=log_file,
            level="ERROR",
            message_contains="Auth",
            has_keys=["user_id"],
            missing_keys=["session_id"],
        )
        assert len(results) == 1
        assert results[0]["user_id"] == "123"
        assert results[0]["request_id"] == "abc"
        assert "session_id" not in results[0]
    finally:
        Path(log_file).unlink()


def test_integration_log_and_search(caplog):
    with tempfile.NamedTemporaryFile(mode="w+", suffix=".log", delete=False) as f:
        log_file = f.name

    try:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(logging.Formatter("%(message)s"))
        Logger._ensure_configured()
        Logger._logger.addHandler(file_handler)

        Logger.bind("request_id", "abc123")
        Logger.info("First message")
        Logger.error("Error message")
        Logger.info(message="Second message", user_id="user456")

        Logger._logger.removeHandler(file_handler)
        file_handler.close()

        results = Logger.search(log_file=log_file)
        assert len(results) == 3

        error_results = Logger.search(log_file=log_file, level="ERROR")
        assert len(error_results) == 1
        assert error_results[0]["message"] == "Error message"

        context_results = Logger.search(log_file=log_file, context={"request_id": "abc123"})
        assert len(context_results) == 3

        # Test has_keys filter
        user_results = Logger.search(log_file=log_file, has_keys=["user_id"])
        assert len(user_results) == 1
        assert user_results[0]["user_id"] == "user456"

        # Test missing_keys filter
        no_user_results = Logger.search(log_file=log_file, missing_keys=["user_id"])
        assert len(no_user_results) == 2

    finally:
        Path(log_file).unlink()
