# Utils

A Python utility library providing static utility classes for common operations on built-in Python types.

## Installation

```bash
# Using uv
uv pip install -e .

# Or using pip
pip install -e .

# With dev dependencies (for testing)
uv pip install -e ".[dev]"
# or
pip install -e ".[dev]"
```

## Testing

The project includes a comprehensive test suite with 419 tests covering all utilities, edge cases, and error conditions.

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=utils --cov-report=html

# Run specific test file
pytest tests/test_string.py

# Run with verbose output
pytest -v
```

## Usage

The library provides static utility classes for common operations on built-in Python types. All methods are static and use keyword-only arguments for clarity.

### String Utilities

The `String` class provides static methods for text manipulation:

```python
from utils import String

# Truncate strings (keyword-only arguments)
text = "This is a very long string that needs truncation"
short = String.truncate(text, length=20)  # "This is a very long..."

# Truncate by word count
text = "Hello world from Python utils"
short = String.truncate_words(text, count=2)  # "Hello world..."

# Case conversions
String.camel_case("hello world")  # "helloWorld"
String.snake_case("Hello World")  # "hello_world"
String.kebab_case("Hello World")  # "hello-world"
String.title_case("hello world")  # "Hello World"

# String manipulation
String.reverse("hello")  # "olleh"
String.remove_whitespace("hello world")  # "helloworld"
String.pad_left("hello", width=10, fill_char="*")  # "*****hello"
String.pad_right("hello", width=10, fill_char="*")  # "hello*****"
String.pad_center("hello", width=10, fill_char="*")  # "**hello***"

# Prefix/suffix removal
String.remove_prefix("prefix_hello", prefix="prefix_")  # "hello"
String.remove_suffix("hello_suffix", suffix="_suffix")  # "hello"

# Text wrapping
String.wrap("This is a long line of text", width=10)
# ["This is a", "long line", "of text"]

# Create URL slug
String.slug("Hello World! This is a Test")  # "hello-world-this-is-a-test"

# Hashing
String.hash("hello")  # "5d41402abc4b2a76b9719d911017c592" (MD5)

# Validation
String.is_email("user@example.com")  # True
String.is_url("https://example.com")  # True

# Extraction
text = "Contact us at info@example.com or support@example.com"
String.extract_emails(text)  # ["info@example.com", "support@example.com"]

text = "Visit https://example.com and https://test.com"
String.extract_urls(text)  # ["https://example.com", "https://test.com"]
```

### Integer Utilities

The `Integer` class provides static methods for number operations:

```python
from utils import Integer

# Number properties
Integer.is_even(4)  # True
Integer.is_odd(5)  # True
Integer.is_prime(7)  # True

# Clamping
Integer.clamp(15, min_val=0, max_val=10)  # 10
Integer.clamp(-5, min_val=0, max_val=10)  # 0

# Conversions
Integer.to_roman(4)  # "IV"
Integer.to_words(123)  # "one hundred twenty-three"

# Math operations
Integer.factorial(5)  # 120
Integer.gcd(48, 18)  # 6
Integer.lcm(12, 18)  # 36
Integer.is_power_of(8, base=2)  # True

# Digit manipulation
Integer.digits(123)  # [1, 2, 3]
Integer.reverse(123)  # 321

# Bytes to human readable
Integer.bytes_to_human(1536)  # "1.50 KB"
Integer.bytes_to_human(1048576)  # "1.00 MB"

# Percentage calculation
Integer.percentage(25, total=200)  # 12.5
```

### Iterable Utilities

The `Iterable` class provides static methods for collection operations:

```python
from utils import Iterable

# Chunking and flattening
Iterable.chunk([1, 2, 3, 4, 5], size=2)  # [[1, 2], [3, 4], [5]]
Iterable.flatten([[1, 2], [3, 4]])  # [1, 2, 3, 4]

# Getting items
Iterable.first([1, 2, 3])  # 1
Iterable.last([1, 2, 3])  # 3

# Filtering and uniqueness
Iterable.unique([1, 2, 2, 3, 1])  # [1, 2, 3]
Iterable.compact([1, None, 2, None, 3])  # [1, 2, 3]

# Grouping and partitioning
Iterable.group_by([1, 2, 3, 4], key=lambda x: x % 2)  # {0: [2, 4], 1: [1, 3]}
Iterable.partition([1, 2, 3, 4, 5], predicate=lambda x: x % 2 == 0)  # ([2, 4], [1, 3, 5])

# Extracting from dicts
Iterable.pluck([{"name": "Alice"}, {"name": "Bob"}], key="name")  # ['Alice', 'Bob']

# Aggregations
Iterable.sum_by([1, 2, 3, 4])  # 10
Iterable.average([1, 2, 3, 4])  # 2.5
Iterable.count_by([1, 2, 2, 3])  # {1: 1, 2: 2, 3: 1}

# Sorting
Iterable.sort_by([{"age": 30}, {"age": 25}], key="age")  # [{"age": 25}, {"age": 30}]

# Slicing
Iterable.take([1, 2, 3, 4, 5], n=3)  # [1, 2, 3]
Iterable.drop([1, 2, 3, 4, 5], n=2)  # [3, 4, 5]
```

### Datetime Utilities

The `Datetime` class provides static methods for date/time operations:

```python
from utils import Datetime
from datetime import datetime

# Parsing
dt = Datetime.parse("2024-01-01 12:00:00")
dt = Datetime.from_iso("2024-01-01T12:00:00Z")
dt = Datetime.from_timestamp(1704110400)
dt = Datetime.now()  # Current datetime

# Formatting
dt = datetime(2024, 1, 1, 12, 0, 0)
Datetime.format(dt)  # "2024-01-01 12:00:00"
Datetime.format(dt, format_str="%Y-%m-%d")  # "2024-01-01"
Datetime.to_iso(dt)  # "2024-01-01T12:00:00"
Datetime.to_rfc3339(dt)  # "2024-01-01T12:00:00Z"
Datetime.to_readable(dt)  # "January 1, 2024 at 12:00 PM"

# Relative time
from datetime import timedelta
past_dt = datetime.now() - timedelta(hours=2)
Datetime.human_time(past_dt)  # "2 hours ago"

# Day boundaries
dt = datetime(2024, 1, 1, 14, 30, 0)
Datetime.start_of_day(dt)  # datetime(2024, 1, 1, 0, 0)
Datetime.end_of_day(dt)  # datetime(2024, 1, 1, 23, 59, 59, 999999)

# Week boundaries
Datetime.start_of_week(dt)  # Monday at 00:00:00
Datetime.end_of_week(dt)  # Sunday at 23:59:59

# Month/Year boundaries
Datetime.start_of_month(dt)  # First day of month
Datetime.end_of_month(dt)  # Last day of month
Datetime.start_of_year(dt)  # January 1st
Datetime.end_of_year(dt)  # December 31st

# Date arithmetic
Datetime.add_days(dt, days=5)  # Add 5 days
Datetime.add_hours(dt, hours=2)  # Add 2 hours
Datetime.add_weeks(dt, weeks=1)  # Add 1 week
Datetime.add_months(dt, months=1)  # Add 1 month
Datetime.add_years(dt, years=1)  # Add 1 year

# Comparisons
Datetime.is_weekend(dt)  # False (if weekday)
Datetime.is_weekday(dt)  # True
Datetime.days_between(dt, datetime(2024, 1, 5))  # 4
```

### Dict Utilities

The `Dict` class provides static methods for dictionary operations:

```python
from utils import Dict

# Picking and omitting keys
d = {"a": 1, "b": 2, "c": 3}
Dict.pick(d, "a", "c")  # {'a': 1, 'c': 3}
Dict.omit(d, "a", "c")  # {'b': 2}

# Deep get/set
d = {"user": {"profile": {"name": "Alice"}}}
Dict.deep_get(d, path="user.profile.name")  # "Alice"
Dict.deep_set(d, path="user.profile.email", value="alice@example.com")

# Merging
d1 = {"a": 1, "b": {"c": 2}}
d2 = {"b": {"d": 3}, "e": 4}
Dict.merge(d1, d2, deep=True)  # Deep merge nested dicts

# Transformations
d = {"a": 1, "b": 2, "c": 3}
Dict.map_values(d, func=lambda x: x * 2)  # {'a': 2, 'b': 4, 'c': 6}
Dict.map_keys(d, func=str.upper)  # {'A': 1, 'B': 2, 'C': 3}
Dict.filter(d, predicate=lambda k, v: v > 1)  # {'b': 2, 'c': 3}
Dict.invert(d)  # {1: 'a', 2: 'b', 3: 'c'}

# Flattening
d = {"a": {"b": {"c": 1}}}
Dict.flatten(d)  # {'a.b.c': 1}
Dict.unflatten({"a.b.c": 1})  # {'a': {'b': {'c': 1}}}

# Utilities
d = {"a": 1, "b": None, "c": 3}
Dict.compact(d)  # {'a': 1, 'c': 3} - removes None values
Dict.defaults(d, defaults={"d": 4})  # Add default values for missing keys
```

### Path Utilities

The `Path` class provides static methods for filesystem operations:

```python
from utils import Path

# Read and write files
Path.write("./data/file.txt", content="Hello World")
content = Path.read("./data/file.txt")  # "Hello World"

# Read and write lines
lines = ["line1", "line2", "line3"]
Path.write_lines("./data/file.txt", lines=lines)
content = Path.read_lines("./data/file.txt")  # ["line1", "line2", "line3"]

# JSON operations
data = {"name": "Alice", "age": 30}
Path.write_json("./data/file.json", data=data)
content = Path.read_json("./data/file.json")  # {"name": "Alice", "age": 30}

# Path properties
Path.extension("./data/file.txt")  # "txt"
Path.get_stem("./data/file.txt")  # "file"

# File management
Path.ensure_dir("./data/subdir")  # Create directory if it doesn't exist
Path.copy("./source.txt", "./dest.txt")
Path.move("./old.txt", "./new.txt")
Path.rm("./file.txt")
Path.size("./file.txt")  # File size in bytes
```

### Random Utilities

The `Random` class provides static methods for random generation:

```python
from utils import Random

# Generate random strings
Random.string(length=10)  # "aB3dE5fG7h"
Random.string(length=10, chars="01")  # "0110101001"

# Generate random numbers
Random.int(min_val=1, max_val=100)  # Random int between 1-100
Random.float(min_val=0.0, max_val=1.0)  # Random float between 0-1

# Random choices
Random.choice([1, 2, 3, 4, 5])  # Random item from list
Random.sample([1, 2, 3, 4, 5], k=3)  # 3 random items (without replacement)
Random.shuffle([1, 2, 3, 4, 5])  # Shuffled list

# UUIDs
Random.uuid4()  # UUID version 4 (random)
Random.uuid1()  # UUID version 1 (time-based)
Random.uuid_string()  # UUID as string without dashes
```

### Validator Utilities

The `Validator` class provides static validation methods:

```python
from utils import Validator

# Email validation
Validator.email("user@example.com")  # True
Validator.email("invalid")  # False

# URL validation
Validator.url("https://example.com")  # True

# Phone number validation
Validator.phone("+1-555-123-4567")  # True

# UUID validation
Validator.uuid("550e8400-e29b-41d4-a716-446655440000")  # True

# Credit card validation (Luhn algorithm)
Validator.credit_card("4532015112830366")  # True

# Hex color validation
Validator.hex_color("#ff0000")  # True
Validator.hex_color("#f00")  # True (3-digit format)

# IPv4 validation
Validator.ipv4("192.168.1.1")  # True

# Check if empty
Validator.empty("")  # True
Validator.empty([])  # True
Validator.empty(None)  # True

# Numeric validation
Validator.numeric("123.45")  # True
Validator.integer("123")  # True
```

### Decorator Utilities

The `Decorators` class provides static decorator methods:

```python
from utils import Decorators

# Debounce function calls (delays execution until calls stop)
@Decorators.debounce(delay=0.5)
def handle_input():
    print("Input handled")

# Throttle function calls (limits execution rate)
@Decorators.throttle(delay=0.5)
def handle_scroll():
    print("Scroll handled")

# Retry with exponential backoff
@Decorators.retry(max_attempts=3, delay=1.0, backoff=2.0)
def unreliable_api_call():
    # Will retry up to 3 times with increasing delays (1s, 2s, 4s)
    pass

# Memoize function results (caches based on arguments)
@Decorators.memoize
def expensive_function(x):
    return x * 2

# Call function only once (subsequent calls return cached result)
@Decorators.once
def initialize():
    print("Initialized")
```

### Regex Utilities

The `Regex` class provides static pattern matching methods:

```python
from utils import Regex

# Match patterns
Regex.match(pattern=r"^\d+$", text="123")  # Match object (or None)
Regex.search(pattern=r"\d+", text="abc123def")  # Match object (or None)

# Find all matches
Regex.findall(pattern=r"\d+", text="abc123def456")  # ["123", "456"]

# Replace patterns
Regex.sub(pattern=r"\d+", repl="X", text="abc123def456")  # "abcXdefX"

# Split by pattern
Regex.split(pattern=r"\s+", text="hello  world")  # ["hello", "world"]

# Extract groups
match = Regex.search(pattern=r"(\d+)-(\d+)", text="123-456")
Regex.groups(match)  # ("123", "456")
Regex.groupdict(match)  # {} or dict of named groups

# Validate regex pattern
Regex.is_valid(r"^\d+$")  # True
Regex.is_valid(r"[invalid(")  # False
```

### Logger Utilities

The `Logger` class provides static methods for structured JSON logging with persistent context management:

```python
from utils import Logger

# Three flexible input formats for all log levels

# 1. Simple string message
Logger.info("User logged in")
# Output: {"timestamp": "2025-11-15T10:30:00.123456+00:00", "level": "INFO", "message": "User logged in"}

# 2. Dictionary format
Logger.info({"message": "User logged in", "user_id": 123, "ip": "192.168.1.1"})
# Output: {"timestamp": "2025-11-15T10:30:00.123456+00:00", "level": "INFO", "message": "User logged in", "user_id": 123, "ip": "192.168.1.1"}

# 3. Keyword arguments
Logger.info(message="User logged in", user_id=123, ip="192.168.1.1")
# Same output as dictionary format

# All log levels supported
Logger.debug("Debug message")
Logger.info("Info message")
Logger.warning("Warning message")
Logger.error("Error message")
Logger.critical("Critical message")

# Persistent context - automatically added to all subsequent logs
Logger.bind("user_id", 123)
Logger.bind("session_id", "abc-def-ghi")
Logger.info("Action performed")
# {"timestamp": "...", "level": "INFO", "user_id": 123, "session_id": "abc-def-ghi", "message": "Action performed"}

# Bind multiple keys at once
Logger.bind_multiple(user_id=123, session_id="abc-def-ghi", environment="production")

# Automatic key normalization (camelCase, PascalCase, kebab-case → snake_case)
Logger.bind("userId", 123)        # Normalized to "user_id"
Logger.bind("SessionID", "abc")   # Normalized to "session_id"
Logger.bind("api-key", "xyz")     # Normalized to "api_key"

# Scoped context with context managers
with Logger.context(request_id="req-123", endpoint="/api/users"):
    Logger.info("Processing request")
    # {"timestamp": "...", "level": "INFO", "request_id": "req-123", "endpoint": "/api/users", "message": "Processing request"}
# Context automatically cleared after the with block

# Nested context managers
Logger.bind("user_id", 123)
with Logger.context(request_id="req-123"):
    with Logger.context(operation="update"):
        Logger.info("Updating user")
        # Includes: user_id, request_id, and operation
    # operation removed, user_id and request_id remain
# request_id removed, user_id remains

# Get current context
context = Logger.get_context()  # Returns copy of current context dict

# Remove specific context keys
Logger.unbind("user_id")

# Clear all context
Logger.clear_context()

# Custom types are automatically handled (tuples, sets, datetime, custom objects)
from datetime import datetime

Logger.info(
    message="Event occurred",
    coordinates=(40.7128, -74.0060),  # Tuple → JSON array
    tags={"python", "logging"},        # Set → JSON array
    timestamp=datetime.now(),          # datetime → ISO string
)

# Custom objects with to_dict() method
class User:
    def to_dict(self):
        return {"id": 123, "name": "Alice"}

Logger.info(message="User created", user=User())
# {"timestamp": "...", "level": "INFO", "message": "User created", "user": {"id": 123, "name": "Alice"}}

# Search and parse log files
results = Logger.search(
    "app.log",
    level="ERROR",                    # Filter by log level
    start_time="2025-11-15T00:00:00", # Filter by time range
    end_time="2025-11-15T23:59:59",
    message_contains="database",      # Search message text
    message_pattern=r"error \d+",     # Regex pattern matching
    context={"user_id": 123},         # Filter by context values
    has_keys=["user_id", "request_id"],  # Must have these keys
    missing_keys=["error_code"]       # Must NOT have these keys
)
# Returns list of matching log entries as dicts

# Find all logs that have a specific key
user_logs = Logger.search("app.log", has_keys=["user_id"])

# Find all logs missing a specific key
anonymous_logs = Logger.search("app.log", missing_keys=["user_id"])

# Combine filters: ERROR logs with user_id but no session_id
filtered = Logger.search(
    "app.log",
    level="ERROR",
    has_keys=["user_id"],
    missing_keys=["session_id"]
)

# Thread-safe logging - each thread has isolated context
import threading

def worker():
    Logger.bind("thread_id", threading.get_ident())
    Logger.info("Worker started")  # Only includes this thread's context

threading.Thread(target=worker).start()
```

### Encoding/Decoding Utilities

The `Encode` and `Decode` classes provide static methods for encoding and decoding operations:

```python
from utils import Encode, Decode

# Base64 encoding/decoding
encoded = Encode.base64("Hello World")  # "SGVsbG8gV29ybGQ="
decoded = Decode.base64(encoded)  # "Hello World"

# URL encoding/decoding
encoded = Encode.url("hello world")  # "hello+world"
decoded = Decode.url(encoded)  # "hello world"

# HTML entity encoding/decoding
encoded = Encode.html("<script>alert('XSS')</script>")
# "&lt;script&gt;alert(&#x27;XSS&#x27;)&lt;/script&gt;"
decoded = Decode.html(encoded)  # "<script>alert('XSS')</script>"

# Defang/Fang URLs and IPs (for security analysis and threat intelligence)
defanged = Encode.defang("https://malicious-site.com")  # "hxxps://malicious-site[.]com"
defanged_ip = Encode.defang("192.168.1.1")  # "192[.]168[.]1[.]1"
fanged = Decode.fang("hxxps://malicious-site[.]com")  # "https://malicious-site.com"
fanged_ip = Decode.fang("192[.]168[.]1[.]1")  # "192.168.1.1"
```

## Features

- **Static Utility Classes**: Pure static methods with no inheritance - clean, functional API
- **14 Utility Classes**: String, Integer, Iterable, Dict, Datetime, Path, FileIO, Regex, Random, Validator, Decorators, Logger, Encode, Decode
- **String Utilities** (21 methods): Truncation, case conversions, slug generation, padding, validation, email/URL extraction, hashing
- **Integer Utilities** (15 methods): Properties (even/odd/prime), clamping, conversions (roman/words), math operations, byte formatting, percentages
- **Iterable Utilities** (19 methods): Chunking, flattening, filtering, grouping, partitioning, aggregations, sorting
- **Dict Utilities** (15 methods): Pick/omit keys, deep get/set, merging, transformations, flattening/unflattening
- **Datetime Utilities** (28 methods): Parsing, formatting, relative time, day/week/month/year boundaries, date arithmetic
- **Path Utilities** (11 methods): File I/O for text/lines/JSON, file management (copy/move/delete), path operations
- **Random Utilities** (9 methods): String/number generation, choices, shuffling, UUIDs
- **Validator Utilities** (10 methods): Email, URL, phone, UUID, credit card, hex color, IPv4, empty/numeric checks
- **Decorator Utilities** (5 methods): Debounce, throttle, retry with backoff, memoize, once
- **Regex Utilities** (8 methods): Pattern matching, searching, replacing, splitting, group extraction, validation
- **Logger Utilities**: Structured JSON logging with thread-local context, key normalization, log searching, custom type handling
- **Encode/Decode Utilities**: Base64, URL, HTML encoding/decoding, and defang/fang for security analysis
- **Keyword-Only Arguments**: All parameters (except first) are keyword-only for clarity and safety
- **Type Hints**: Complete type annotations for all methods
- **Zero Dependencies**: No external runtime dependencies required (optional: arrow for enhanced datetime parsing)
- **Comprehensive Tests**: 419 tests covering all utilities, edge cases, and error conditions

