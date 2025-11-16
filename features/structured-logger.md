# Feature Plan: Structured Logger with Persistent Context

**Created**: 2025-11-15
**Updated**: 2025-11-15

## Changelog
- **2025-11-15**: Added flexible logging API supporting string, dict, and keyword arguments. Added key normalization for consistent, parseable output.
- **2025-11-15**: Added log parsing/searching capabilities to query logged messages with flexible filtering options. Clarified level-based filtering behavior (inherited from Python logging).
- **2025-11-15**: Added custom JSON encoder to handle non-serializable types (tuples, Arrow datetimes, custom objects) with graceful fallback to string representation.

## Summary

Add a structured logging utility class that normalizes log message format and supports persistent key-value context. The logger will allow setting contextual key-value pairs that persist across multiple log calls until explicitly reset or removed, enabling consistent metadata tracking throughout application flows (such as request IDs, user IDs, session IDs, etc.).

The logger provides a flexible API accepting multiple input formats: simple strings, dictionaries, or keyword arguments. All keys are automatically normalized to snake_case for consistent, easily parseable log output. Additionally, the logger provides log parsing and searching capabilities to query previously logged messages based on various criteria.

This solves the problem of inconsistent log formatting and the burden of manually passing context variables to every log statement. With persistent context, developers can set tracking metadata once and have it automatically included in all subsequent logs. The built-in log search functionality makes it easy to find and filter logged messages without external tools.

## Acceptance Criteria

- [ ] Logger class follows static utility class pattern consistent with other utils
- [ ] Supports standard log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- [ ] All log output is structured (JSON format by default)
- [ ] Persistent context can be set with key-value pairs
- [ ] Persistent context is included in all log messages until cleared or reset
- [ ] Individual context keys can be added, updated, or removed independently
- [ ] All context can be cleared at once
- [ ] Log messages include timestamp, level, message, and any context
- [ ] Thread-safe context management for multi-threaded applications
- [ ] Context can be scoped using context manager pattern
- [ ] **[Updated]** Logging methods accept three input formats: string, dict, or keyword arguments
- [ ] **[Updated]** `Logger.info("message")` logs with message field from string argument
- [ ] **[Updated]** `Logger.info({"message": "text"})` logs with all dict fields
- [ ] **[Updated]** `Logger.info(message="text")` logs with message field from keyword argument
- [ ] **[Updated]** All three formats produce identical JSON output structure
- [ ] **[Updated]** All context and log keys are automatically normalized to snake_case
- [ ] **[Updated]** Key normalization handles camelCase, PascalCase, kebab-case, spaces, and special characters
- [ ] **[Updated]** Reserved keys (timestamp, level, message) cannot be overridden by user
- [ ] **[Updated]** Log output is consistently formatted for easy parsing and readability
- [ ] **[New]** Logger can parse and search through logged messages from log files
- [ ] **[New]** Search supports filtering by log level (INFO, WARNING, ERROR, etc.)
- [ ] **[New]** Search supports filtering by time range (start time, end time)
- [ ] **[New]** Search supports filtering by message content (text search/regex)
- [ ] **[New]** Search supports filtering by context fields (key-value matching)
- [ ] **[New]** Search returns parsed log entries as structured data (list of dicts)
- [ ] **[New]** Search can combine multiple filters (AND logic)
- [ ] **[New]** Level-based filtering during logging leverages Python logging's built-in level filtering (automatic)
- [ ] **[New]** Custom JSON encoder handles non-serializable types gracefully
- [ ] **[New]** Tuples are converted to lists in JSON output
- [ ] **[New]** Arrow datetime objects are converted to ISO 8601 strings
- [ ] **[New]** Custom objects with `__dict__` are serialized as dictionaries
- [ ] **[New]** Objects with `__str__` method fall back to string representation
- [ ] **[New]** JSON encoder is extensible for additional type support
- [ ] Comprehensive test coverage for all logging and context operations
- [ ] README documentation includes usage examples

## Scope/Non-Goals

### In Scope
- Static Logger utility class with standard log level methods
- Persistent context storage using thread-local storage for thread safety
- Methods to add, update, remove, and clear context key-value pairs
- Context manager for scoped context (automatically cleans up after scope)
- Structured output formatting (JSON by default)
- Integration with Python's standard logging module
- Configuration for output format, log level, and destination
- Helper methods for common patterns (with_context, bind, unbind)
- **[Updated]** Flexible logging API accepting strings, dicts, or keyword arguments
- **[Updated]** Automatic key normalization to snake_case for consistency
- **[Updated]** Protection of reserved keys (timestamp, level, message)
- **[New]** Log parsing and searching functionality to query logged messages
- **[New]** Multiple filter options: level, time range, message content, context fields
- **[New]** Automatic level-based filtering leveraging Python logging's setLevel() mechanism
- **[New]** Custom JSON encoder class to handle non-serializable types
- **[New]** Support for tuples, Arrow datetimes, sets, and custom objects in log data
- **[New]** Graceful fallback to string representation for unknown types
- Full test suite covering logging and context management

### Non-Goals
- Log aggregation or shipping to external services (users can integrate with existing tools)
- Log rotation or file management (use Python's logging handlers)
- Custom log formatters beyond JSON and basic string formats
- Performance monitoring or metrics collection
- Real-time log streaming or tailing (can be added later)
- Async logging support (can be added later if needed)
- Custom log levels beyond standard Python levels
- Advanced query language (SQL-like syntax) for log searching
- Log indexing or database storage for fast searches
- Distributed log searching across multiple files/servers

## Files to Modify

### Files to Create
- **utils/logger.py** - New static Logger utility class with methods for logging at different levels, managing persistent context, and formatting structured output. Will include thread-local storage for context isolation and custom JSON encoder.
- **utils/json_encoder.py** - Custom JSON encoder class that extends json.JSONEncoder to handle non-serializable types like tuples, Arrow datetime objects, sets, and custom objects with graceful fallback behavior.
- **tests/test_logger.py** - Comprehensive test suite covering all log levels, context management, thread safety, context managers, and output formatting.
- **tests/test_json_encoder.py** - Test suite for custom JSON encoder covering all supported type conversions and edge cases.

### Files to Update
- **utils/__init__.py** - Add import for Logger class and include it in __all__ exports list
- **README.md** - Add new "Logger Utilities" section with examples showing basic logging, persistent context usage, scoped context with context managers, and thread-safe patterns

## Design/Approach

The Logger will be implemented as a static utility class following the existing patterns in this library. It will wrap Python's standard logging module while adding structured output and persistent context capabilities.

### Key Design Decisions

**1. Static Utility Class Pattern**
- Follow existing library convention with static methods
- No instance creation required, simple to use: `Logger.info("message")`
- Consistent with String, Integer, Iterable, etc. classes

**2. Thread-Local Context Storage**
- Use `threading.local()` to store context dictionaries per thread
- Prevents context leakage between threads in multi-threaded applications
- Each thread maintains its own isolated context

**3. Integration with Standard Logging**
- Build on top of Python's `logging` module rather than replacing it
- Leverage existing handlers, formatters, and configuration
- Users can configure output destination (stdout, file, etc.) using standard logging setup

**4. JSON Structured Output**
- Default to JSON format for machine-readable logs
- Include fields: timestamp, level, message, context (merged with persistent context)
- Allow fallback to simple string format if needed

**5. Context Manager for Scoped Context**
- Provide `Logger.context()` context manager for temporary context
- Automatically removes scoped context when exiting the with-block
- Useful for request-scoped or function-scoped metadata

**6. Explicit Context Management Methods**
- `Logger.bind(key, value)` - Add or update a single context key
- `Logger.bind_multiple(**kwargs)` - Add or update multiple context keys at once
- `Logger.unbind(key)` - Remove a specific context key
- `Logger.clear_context()` - Remove all context keys
- `Logger.get_context()` - Return current context dictionary (for inspection)

**7. Flexible Logging API** **[Updated: 2025-11-15]**
- Accept three input formats for maximum flexibility:
  1. **String argument**: `Logger.info("Processing request")` → Sets message field automatically
  2. **Dict argument**: `Logger.info({"message": "Processing request", "user_id": "123"})` → Uses all dict keys
  3. **Keyword arguments**: `Logger.info(message="Processing request", user_id="123")` → Named parameters
- All three formats produce identical JSON output structure
- String format is convenient for simple messages
- Dict and keyword formats allow passing additional fields inline
- Fields from all formats are merged with persistent context

**8. Key Normalization** **[Updated: 2025-11-15]**
- Automatically normalize all keys to snake_case for consistency
- Conversion rules:
  - `camelCase` → `camel_case`
  - `PascalCase` → `pascal_case`
  - `kebab-case` → `kebab_case`
  - `spaces here` → `spaces_here`
  - Multiple consecutive separators collapsed to single underscore
  - Leading/trailing underscores removed
  - All lowercase output
- Normalization applies to both persistent context keys and inline log fields
- Reserved keys protected: `timestamp`, `level`, `message` cannot be overridden
- Keys normalized before storage to ensure consistent lookups and output

**9. Log Parsing and Searching** **[New: 2025-11-15]**
- Provide `Logger.search()` method to query logged messages from log files
- Parse JSON log lines back into structured dictionaries
- Support multiple filter types that can be combined:
  - **Level filter**: Match specific log levels (INFO, WARNING, ERROR, etc.)
  - **Time range filter**: Match logs within start/end timestamps
  - **Message filter**: Match message content using substring or regex patterns
  - **Context filter**: Match specific context field values (key=value pairs)
- Return results as list of dictionaries (structured data)
- Handle malformed log lines gracefully (skip non-JSON lines)
- Leverage Python logging's built-in setLevel() for automatic level-based filtering during log writing
  - Logger.setLevel(logging.WARNING) will prevent INFO/DEBUG from being written
  - Search only queries what was actually written to the file
  - No need to re-implement level filtering in search - it's already filtered at write time

**10. Custom JSON Encoder** **[New: 2025-11-15]**
- Create dedicated JsonEncoder class extending json.JSONEncoder
- Handle common non-serializable types automatically:
  - **Tuples**: Convert to lists `(1, 2, 3)` → `[1, 2, 3]`
  - **Sets**: Convert to lists `{1, 2, 3}` → `[1, 2, 3]`
  - **Arrow datetime objects**: Convert to ISO 8601 strings using `.isoformat()`
  - **datetime.datetime**: Convert to ISO 8601 strings
  - **datetime.date**: Convert to ISO 8601 date strings
  - **Custom objects with `__dict__`**: Serialize object's dictionary representation
  - **Objects with `to_dict()` method**: Call method and use result
  - **Fallback**: Use `str(obj)` for any unhandled type
- Use encoder in Logger's JSON formatting to prevent serialization errors
- Allow users to pass custom context values without worrying about JSON compatibility
- Extensible design - easy to add support for new types in future

### Architecture Impact

This adds a new top-level utility class to the library. It has minimal impact on existing code since it's a new module with no dependencies on other utility classes. Users can adopt it incrementally without affecting existing functionality.

The Logger will be self-contained and follow the same patterns as other static utility classes, making it easy to understand for users already familiar with the library.

### API Examples **[New: 2025-11-15]**

The flexible API provides three equivalent ways to log:

**1. String format (simple messages):**
```
Logger.info("Processing request")
→ {"timestamp": "2025-11-15T10:30:00", "level": "INFO", "message": "Processing request", ...context}
```

**2. Dict format (multiple fields):**
```
Logger.info({"message": "Processing request", "user_id": "123", "action": "login"})
→ {"timestamp": "2025-11-15T10:30:00", "level": "INFO", "message": "Processing request", "user_id": "123", "action": "login", ...context}
```

**3. Keyword format (named parameters):**
```
Logger.info(message="Processing request", user_id="123", action="login")
→ {"timestamp": "2025-11-15T10:30:00", "level": "INFO", "message": "Processing request", "user_id": "123", "action": "login", ...context}
```

**Key normalization examples:**
```
Logger.bind("userId", "123")         → stored as "user_id"
Logger.bind("requestID", "abc")      → stored as "request_id"
Logger.bind("some-value", "xyz")     → stored as "some_value"
Logger.bind("my  Weird__key", "x")   → stored as "my_weird_key"
```

**Merging behavior:**
```
# Set persistent context
Logger.bind("request_id", "abc123")

# Log with additional inline field
Logger.info(message="Processing", user_id="user456")

# Output includes both:
→ {"timestamp": "...", "level": "INFO", "message": "Processing", "request_id": "abc123", "user_id": "user456"}
```

**Custom type handling examples:** **[New: 2025-11-15]**
```
# Tuples are automatically converted to lists
Logger.info(message="Coordinates", position=(10, 20, 30))
→ {"timestamp": "...", "level": "INFO", "message": "Coordinates", "position": [10, 20, 30]}

# Sets are converted to lists
Logger.info(message="Tags", tags={"python", "logging", "json"})
→ {"timestamp": "...", "level": "INFO", "message": "Tags", "tags": ["python", "logging", "json"]}

# Arrow datetime objects (if arrow is installed)
import arrow
Logger.info(message="Event", event_time=arrow.now())
→ {"timestamp": "...", "level": "INFO", "message": "Event", "event_time": "2025-11-15T10:30:00+00:00"}

# Custom objects with to_dict() method
class User:
    def to_dict(self):
        return {"id": 123, "name": "Alice"}

Logger.info(message="User action", user=User())
→ {"timestamp": "...", "level": "INFO", "message": "User action", "user": {"id": 123, "name": "Alice"}}

# Unknown types fall back to string representation
Logger.info(message="Data", value=object())
→ {"timestamp": "...", "level": "INFO", "message": "Data", "value": "<object object at 0x...>"}
```

**Search API examples:** **[New: 2025-11-15]**
```
# Search all ERROR logs
errors = Logger.search(log_file="app.log", level="ERROR")

# Search logs within time range
recent = Logger.search(
    log_file="app.log",
    start_time="2025-11-15T10:00:00",
    end_time="2025-11-15T11:00:00"
)

# Search by message content (substring)
auth_logs = Logger.search(log_file="app.log", message_contains="authentication")

# Search by message content (regex)
pattern_logs = Logger.search(log_file="app.log", message_pattern=r"user_\d+")

# Search by context field
user_logs = Logger.search(log_file="app.log", context={"user_id": "user123"})

# Combine multiple filters (AND logic)
specific_errors = Logger.search(
    log_file="app.log",
    level="ERROR",
    start_time="2025-11-15T10:00:00",
    context={"request_id": "abc123"}
)

# Returns list of parsed log entries:
→ [
    {"timestamp": "2025-11-15T10:05:23", "level": "ERROR", "message": "Failed to authenticate", "request_id": "abc123"},
    {"timestamp": "2025-11-15T10:15:45", "level": "ERROR", "message": "Database timeout", "request_id": "abc123"}
  ]
```

### Data Flow **[Updated: 2025-11-15]**

1. **Setting Context**: User calls `Logger.bind("requestId", "12345")` → Normalizes key to `request_id` → Stores in thread-local storage

2. **Logging with String**:
   - User calls `Logger.info("Processing request")`
   - Logger retrieves thread-local context: `{"request_id": "12345"}`
   - Creates log entry: `{"message": "Processing request"}`
   - Merges context and entry
   - Adds system fields (timestamp, level)
   - Final output: `{"timestamp": "...", "level": "INFO", "message": "Processing request", "request_id": "12345"}`
   - Formats as JSON and outputs via Python logging

3. **Logging with Dict**:
   - User calls `Logger.info({"message": "Processing", "userId": "user123"})`
   - Logger retrieves context: `{"request_id": "12345"}`
   - Normalizes dict keys: `{"message": "Processing", "user_id": "user123"}`
   - Merges context and normalized dict
   - Adds system fields
   - Final output: `{"timestamp": "...", "level": "INFO", "message": "Processing", "request_id": "12345", "user_id": "user123"}`

4. **Logging with Kwargs**:
   - User calls `Logger.info(message="Processing", userId="user123")`
   - Same flow as dict format
   - Kwargs converted to dict, keys normalized, merged with context

5. **Scoped Context**: User enters `with Logger.context(userId="user123"):` → Normalizes to `user_id` → Adds temporary context → Executes code with combined context → Removes temporary context on exit

6. **Clearing**: User calls `Logger.clear_context()` → Empties thread-local context storage

7. **Searching Logs** **[New: 2025-11-15]**:
   - User calls `Logger.search(log_file="app.log", level="ERROR", context={"user_id": "123"})`
   - Logger opens log file and reads line by line
   - Each line is parsed as JSON into a dictionary
   - Malformed/non-JSON lines are skipped with warning
   - Each parsed entry is checked against all provided filters:
     - Level filter: `entry["level"] == "ERROR"`
     - Context filter: `entry.get("user_id") == "123"`
   - Entries matching ALL filters are added to results list
   - Returns list of matching log entries as dictionaries
   - Note: Level filtering during logging is automatic via Python logging's setLevel() - search only sees what was written

## Tests to Add/Update

### Unit Tests (tests/test_logger.py) **[Updated: 2025-11-15]**
- Test basic logging at each level (debug, info, warning, error, critical)
- Test JSON output format structure and field presence
- Test persistent context binding and unbinding
- Test context appears in all subsequent log messages
- Test clearing context removes all keys
- Test multiple context keys can coexist
- Test updating existing context keys
- Test thread isolation (context in one thread doesn't affect another)
- Test context manager adds and removes temporary context
- Test nested context managers combine contexts correctly
- Test get_context returns current context dictionary
- Test logging with no context works correctly
- **Test logging with string argument** creates message field
- **Test logging with dict argument** uses all dict fields
- **Test logging with keyword arguments** creates fields from kwargs
- **Test all three input formats produce identical output** when given same data
- **Test key normalization** for camelCase, PascalCase, kebab-case, spaces
- **Test key normalization** removes leading/trailing underscores
- **Test key normalization** collapses multiple separators
- **Test reserved keys** (timestamp, level, message) cannot be overridden
- **Test dict and kwargs merge** with persistent context correctly
- **Test inline fields override** persistent context fields with same key
- Test edge cases (empty context, None values, special characters in keys)
- **Test custom JSON encoder with tuples** converts to lists
- **Test custom JSON encoder with sets** converts to lists
- **Test custom JSON encoder with Arrow datetimes** converts to ISO strings
- **Test custom JSON encoder with datetime objects** converts to ISO strings
- **Test custom JSON encoder with custom objects** (to_dict method, __dict__ attribute)
- **Test custom JSON encoder fallback** uses str() for unknown types
- **Test logger handles non-serializable context values** without errors
- **Test nested structures with mixed types** are properly encoded
- **Test search with no filters** returns all log entries
- **Test search with level filter** returns only matching levels
- **Test search with time range filter** returns logs within start/end times
- **Test search with message_contains filter** returns logs with matching message text
- **Test search with message_pattern filter** (regex) returns logs matching pattern
- **Test search with context filter** returns logs with matching context fields
- **Test search with multiple filters** (AND logic) returns logs matching all criteria
- **Test search with non-existent log file** raises appropriate error
- **Test search handles malformed JSON lines** gracefully (skips with warning)
- **Test search handles empty log file** returns empty list
- **Test search returns structured data** (list of dicts with correct fields)

### Integration Tests
- Test Logger with different Python logging handlers (StreamHandler, FileHandler)
- Test Logger output can be parsed as valid JSON
- Test Logger works correctly in multi-threaded scenarios with concurrent logging
- **Test end-to-end workflow**: Log messages to file, then search and verify results match
- **Test search performance** with large log files (1000+ entries)

### Manual Testing
- Import Logger in Python REPL and verify log output appears correctly
- Test with different log levels and observe filtering behavior
- Test context persistence across multiple log calls
- Verify thread safety by running multi-threaded example
- **Log messages to a file, then use search to query them and verify results**
- **Test search with various filter combinations**
- **Verify search handles real-world log files with mixed content**

## Risks & Rollback

### Risks

**1. Thread-local storage overhead**
- Mitigation: Thread-local storage has minimal overhead; only stores small dictionaries
- Alternative: Could use global dict with thread IDs as keys, but thread-local is cleaner

**2. Memory leaks from abandoned context**
- Mitigation: Provide clear documentation on clearing context; context managers auto-clean
- Mitigation: Thread-local storage automatically cleans up when thread terminates

**3. JSON serialization failures**
- Mitigation: Wrap serialization in try-except, fall back to string representation
- Mitigation: Validate context values are JSON-serializable when binding

**4. Performance impact from JSON formatting**
- Mitigation: JSON formatting is fast for small dictionaries (typical context size)
- Mitigation: Can add string format mode if performance becomes issue

**5. Search performance with large log files** **[New: 2025-11-15]**
- Mitigation: Search reads file line-by-line (streaming) instead of loading entire file into memory
- Mitigation: Document performance characteristics and recommend log rotation for very large files
- Alternative: Could add optional indexing in future if needed

**6. Malformed JSON in log files breaking search** **[New: 2025-11-15]**
- Mitigation: Wrap JSON parsing in try-except, skip malformed lines with warning
- Mitigation: Log parsing errors so users can identify problematic log entries
- User impact: Partial results returned even if some lines are malformed

**7. Non-serializable types causing JSON encoding failures** **[New: 2025-11-15]**
- Mitigation: Custom JSON encoder handles common non-serializable types automatically
- Mitigation: Fallback to string representation ensures encoding never fails
- User impact: All context values are logged, even if type conversion is lossy
- Alternative: Could raise warnings when using fallback str() conversion for debugging

### Rollback Plan

Since this is a new module with no dependencies on existing code:
1. Simply remove `utils/logger.py`, `utils/json_encoder.py`, `tests/test_logger.py`, and `tests/test_json_encoder.py`
2. Remove Logger import from `utils/__init__.py`
3. Remove Logger from __all__ list
4. Remove documentation from README.md
5. No existing code will be affected since this is additive

## Evidence

Relevant files from discovery:

- `utils/__init__.py:1-48` — Shows existing static utility class export pattern that Logger should follow
- `utils/string.py` — Example of static utility class pattern with @staticmethod decorator
- `utils/decorators.py` — Example of utility class that wraps existing Python features (similar to wrapping logging module)
- `.claude/coding_standards.md:11-23` — Confirms OOP preference and static method pattern for utilities
- `tests/test_string.py` — Example test structure to follow for comprehensive test coverage

## Assumptions

1. Users want structured logging in JSON format (industry standard for log aggregation)
2. Thread safety is important for production applications
3. Context should persist across log calls within the same thread/request
4. Python's standard logging module is acceptable as the underlying implementation
5. No external logging dependencies are desired (keep library dependency-free)
6. Context values will be JSON-serializable (strings, numbers, booleans, lists, dicts)
7. Performance is acceptable with JSON formatting (premature optimization avoided)

## Open Questions

1. **Should Logger support async/await patterns?**
   - Async context management with `async with Logger.context()`
   - Decision: Not in initial implementation; can add later if needed

2. **Should there be a simple string format option in addition to JSON?**
   - Decision: Implement JSON as default, add simple string format as configurable option

3. **Should context keys be namespaced to prevent collisions?**
   - e.g., user-provided keys vs. system keys like timestamp
   - Decision: No namespacing in v1; users responsible for key naming; could add prefix option later

4. **Should Logger configure Python logging automatically or require manual setup?**
   - Decision: Auto-configure with sensible defaults (stdout, INFO level) but allow users to configure manually

5. **Should there be convenience methods like Logger.request_context(request_id)?**
   - Decision: Keep API minimal in v1; users can create their own wrappers

6. **How should non-serializable context values be handled?**
   - Decision: Convert to string representation with `str()` and log warning

7. **Should context support nested dictionaries or only flat key-value pairs?**
   - Decision: Support flat key-value in v1 for simplicity; nested values converted to strings

8. **Should Arrow datetime support be optional or required?**
   - Decision: Make it optional - check if Arrow is available before attempting Arrow-specific conversion
   - Fallback to standard datetime handling if Arrow is not installed

## Tasks **[Updated: 2025-11-15]**

1. Create `utils/json_encoder.py` file with JsonEncoder class extending json.JSONEncoder
2. **Implement default method in JsonEncoder** to handle type conversions
3. **Add tuple to list conversion** in encoder
4. **Add set to list conversion** in encoder
5. **Add Arrow datetime detection and conversion** (optional, check if arrow module exists)
6. **Add datetime.datetime to ISO string conversion** in encoder
7. **Add datetime.date to ISO string conversion** in encoder
8. **Add custom object handling** (check for to_dict method, then __dict__ attribute)
9. **Add fallback string conversion** for unhandled types using str()
10. Create comprehensive test suite in `tests/test_json_encoder.py`
11. **Test encoder with tuples** of various sizes
12. **Test encoder with sets** containing different types
13. **Test encoder with Arrow datetimes** (if available)
14. **Test encoder with standard datetime objects**
15. **Test encoder with custom objects** (to_dict method, __dict__ attribute, neither)
16. **Test encoder with nested structures** (list of tuples, dict with sets, etc.)
17. **Test encoder fallback behavior** with exotic types
18. **Test encoder with None values** and edge cases
19. Create `utils/logger.py` file with Logger class skeleton
20. Implement thread-local storage for context using `threading.local()`
21. **Implement key normalization helper method** that converts various formats to snake_case
22. **Update bind and bind_multiple methods** to normalize keys before storage
23. Implement context management methods: bind, bind_multiple, unbind, clear_context, get_context
24. **Implement flexible logging method argument parsing** to detect string, dict, or kwargs input
25. **Add logic to handle string argument** by creating dict with message key
26. **Add logic to handle dict argument** by normalizing all keys
27. **Add logic to handle keyword arguments** by converting to dict and normalizing keys
28. **Add reserved key protection** to prevent overriding timestamp, level, message
29. **Import and use JsonEncoder** in Logger for JSON formatting
30. Implement basic logging methods for each level: debug, info, warning, error, critical
31. Implement JSON formatting for log output with timestamp, level, message, and context fields using JsonEncoder
32. Implement context manager class for scoped context with key normalization (enter/exit methods)
33. Add Logger.context static method that returns context manager instance
34. Implement automatic Python logging configuration with sensible defaults
35. Create comprehensive test suite in `tests/test_logger.py`
36. Test basic logging at all levels
37. **Test all three input formats: string, dict, kwargs**
38. **Test key normalization for various input formats**
39. **Test reserved key protection**
40. **Test that all three formats produce identical output**
41. Test context binding, unbinding, and clearing with normalized keys
42. Test context persistence across multiple log calls
43. Test thread safety with multi-threaded test cases
44. Test context manager scoped context behavior
45. Test nested context managers
46. Test JSON output format and field presence
47. **Test inline fields merge and override behavior with persistent context**
48. **Test logger with non-serializable types in context** (tuples, sets, custom objects)
49. **Test logger output is valid JSON** even with complex types
50. Test edge cases (empty context, None values, special characters in keys)
51. **Implement Logger.search() static method** with log file path parameter
52. **Add log file reading logic** that opens and reads line-by-line (streaming)
53. **Add JSON parsing logic** with error handling for malformed lines
54. **Implement level filter** to match specific log levels
55. **Implement time range filter** to match logs between start/end timestamps
56. **Implement message_contains filter** for substring matching in message field
57. **Implement message_pattern filter** for regex pattern matching in message field
58. **Implement context filter** to match specific context field key-value pairs
59. **Add filter combination logic** (AND - all filters must match)
60. **Add error handling** for non-existent log files with clear error message
61. **Return structured results** as list of dictionaries
62. **Test search with no filters** returns all entries
63. **Test search with level filter** returns correct subset
64. **Test search with time range filter** handles timestamp parsing and comparison
65. **Test search with message filters** (both substring and regex)
66. **Test search with context filter** matches key-value pairs correctly
67. **Test search with combined filters** (multiple filters with AND logic)
68. **Test search error handling** (non-existent file, malformed JSON, empty file)
69. **Test search edge cases** (empty results, partial matches, special characters)
70. **Integration test**: Log to file then search and verify results
71. Add Logger import to `utils/__init__.py`
72. Add Logger to __all__ exports list
73. Update README.md with Logger Utilities section showing all three API formats, custom type handling, and search examples
74. Run full test suite to ensure no regressions
75. Verify Logger can be imported and used in Python REPL with all three formats, custom types, and search functionality

---

**Notes**: This feature will provide a modern, structured logging solution that fits naturally into the existing utility library. The persistent context feature is the key differentiator, making it easy to track request/session metadata throughout application flows without manually passing context everywhere.

The custom JSON encoder ensures that developers can log any type of data without worrying about serialization errors. This is particularly useful when working with complex data structures, datetime objects, or custom classes. The encoder provides sensible defaults while remaining extensible for future type support.
