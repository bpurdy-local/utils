# Utils

A Python utility library providing static utility classes for common operations on built-in Python types.

## Installation

```bash
# Using uv (recommended)
uv pip install -e .

# Or using pip
pip install -e .

# With dev dependencies (for testing)
uv pip install -e ".[dev]"
# or
pip install -e ".[dev]"
```

### Verify Installation

After installing, verify the package is correctly configured:

```bash
# Quick verification
python -c "from utils import String, Integer, Dict, Path, Logger; print('✓ Installation successful!')"

# Or run the import tests
pytest tests/test_imports.py -v
```

This confirms that the `utils` package is properly installed and all utility classes can be imported.

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
String.is_blank("")  # True
String.is_blank("  ")  # True
String.is_blank(None)  # True
String.is_blank("hello")  # False

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

# Finding items
users = [{"name": "Alice", "age": 30}, {"name": "Bob", "age": 25}, {"name": "Charlie", "age": 30}]
Iterable.find_first(users, predicate=lambda u: u["age"] == 30)  # {"name": "Alice", "age": 30}
Iterable.find_last(users, predicate=lambda u: u["age"] == 30)  # {"name": "Charlie", "age": 30}
Iterable.find_all(users, predicate=lambda u: u["age"] == 30)  # [{"name": "Alice", ...}, {"name": "Charlie", ...}]
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
Dict.map_keys(d, func=str.upper)  # {'A': 1, 'B': 2, 'C': 3} useful in combination with the String class
Dict.filter(d, predicate=lambda k, v: v > 1)  # {'b': 2, 'c': 3}
Dict.invert(d)  # {1: 'a', 2: 'b', 3: 'c'}

# Key case transformations
d = {"first_name": "Alice", "last_name": "Smith", "user_data": {"home_address": "123 Main St"}}
Dict.keys_to_camel(d)  # {'firstName': 'Alice', 'lastName': 'Smith', 'userData': {...}}
Dict.keys_to_camel(d, capitalize_first=True)  # {'FirstName': 'Alice', 'LastName': 'Smith', ...}
Dict.keys_to_camel(d, recursive=True)  # Transforms all nested dict keys
Dict.keys_to_snake({"firstName": "Alice", "lastName": "Smith"})  # {'first_name': 'Alice', 'last_name': 'Smith'}

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
Path.extension("./data/file.txt")  # ".txt"
Path.get_stem("./data/file.txt")  # "file"
Path.exists("./data/file.txt")  # True if file or directory exists

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

# Geographic validation
Validator.is_latitude(40.7128)  # True (New York)
Validator.is_latitude(91)  # False (out of range)
Validator.is_latitude(-90, strict=False)  # True (includes boundary)
Validator.is_longitude(-74.0060)  # True
Validator.is_longitude(181)  # False (out of range)
Validator.is_timezone("America/New_York")  # True
Validator.is_timezone("UTC")  # True
Validator.is_timezone("Invalid/Zone")  # False
Validator.is_coordinates(40.7128, -74.0060)  # True (valid lat/lon pair)
```

### Terminal Utilities

The `Terminal` class provides static methods for terminal input, prompts, and formatting:

```python
from utils import Terminal

# Basic text input
name = Terminal.prompt("Enter your name")  # User types: John
port = Terminal.prompt("Enter port", default="8080")  # Press Enter for default

# Prompt with custom validator (returns tuple: (is_valid, error_message))
email = Terminal.prompt(
    "Enter email",
    validator=lambda x: ((True, None) if "@" in x else (False, "Must contain @"))
)

# Yes/no confirmation
if Terminal.confirm("Delete file?"):
    print("Deleting...")
if Terminal.confirm("Continue?", default=True):  # [Y/n] format
    print("Continuing...")

# Password input (hidden)
password = Terminal.password()  # Default message
api_key = Terminal.password("Enter API key")

# Multiple choice selection
env = Terminal.choice("Select environment", choices=["dev", "staging", "prod"])
env = Terminal.choice("Select env", choices=["dev", "prod"], default="dev")

# Numbered selection
idx, option = Terminal.select("Choose option", options=["Apple", "Banana", "Cherry"])
# Displays:
# Choose option:
#   1. Apple
#   2. Banana
#   3. Cherry

# Multi-line input
sql = Terminal.multiline("Enter SQL query", terminator="GO")
# User types multiple lines, ends with "GO"

# Integer input with validation
age = Terminal.prompt_int("Enter age", min_val=0, max_val=120)
port = Terminal.prompt_int("Port", default=8080, min_val=1, max_val=65535)

# Float input with validation
rate = Terminal.prompt_float("Enter rate", min_val=0.0, max_val=1.0)
price = Terminal.prompt_float("Price", default=9.99)

# Custom validation
email = Terminal.validate_input(
    "Enter email",
    validator=lambda x: "@" in x,
    error_message="Must be a valid email"
)

# Terminal formatting
Terminal.clear()  # Clear screen
Terminal.print_line()  # Print horizontal line (80 chars)
Terminal.print_line("=", width=40)  # Custom character and width

# Print text in a box
Terminal.print_box("Hello World")
Terminal.print_box("Multi\nLine\nText", padding=2, width=30)
# ┌──────────────────────────┐
# │                          │
# │  Multi                   │
# │  Line                    │
# │  Text                    │
# │                          │
# └──────────────────────────┘

# Colorize text (ANSI colors)
error_msg = Terminal.colorize("Error", color="red", bold=True)
success_msg = Terminal.colorize("Success", color="green")
highlight = Terminal.colorize("Important", bg_color="yellow", underline=True)
print(error_msg)  # Displays in red and bold

# Progress bar
progress = Terminal.progress_bar(50, 100)
# "50%|█████████████████████████░░░░░░░░░░░░░░░░░░░░░░░░░| 50/100"

progress = Terminal.progress_bar(
    current=75,
    total=100,
    prefix="Downloading:",
    suffix="complete",
    width=30,
    fill="█",
    empty="░"
)
print(progress)  # Displays progress bar with custom formatting
```

**Use cases:**
- Interactive CLI applications
- User input collection with validation
- Configuration wizards
- Installation scripts
- Formatted terminal output
- Progress indicators

### Beacon Utilities

The `Beacon` class provides a global beacon for storing and retrieving application-wide values with optional TTL and statistics tracking:

```python
from utils import Beacon
from datetime import timedelta

# Register values globally (permanent by default)
Beacon.register("api_key", "secret123")
Beacon.register("timeout", 30)

# Register with TTL (time-to-live) for temporary values
# Can use int (seconds) or timedelta for better readability
Beacon.register("temp_token", "xyz", ttl=300)  # 300 seconds (5 minutes)
Beacon.register("cache_data", {"result": 42}, ttl=60)  # 60 seconds

# Or use timedelta for better readability with longer durations
Beacon.register("session", session_data, ttl=timedelta(hours=1))
Beacon.register("temp_cache", data, ttl=timedelta(minutes=30))
Beacon.register("quick_cache", result, ttl=timedelta(days=7))

# Retrieve from anywhere in your code
api_key = Beacon.get("api_key")  # "secret123"
timeout = Beacon.get("timeout", default=60)  # 30
temp_token = Beacon.get("temp_token")  # "xyz" (or None if expired)

# Check existence (automatically filters expired values)
if Beacon.has("api_key"):
    print("API key is configured")

# Organize with namespaces
Beacon.register("bucket", "my-bucket", namespace="aws")
Beacon.register("project", "my-project", namespace="gcp")
Beacon.register("session_id", "abc123", namespace="user", ttl=1800)  # 30 min TTL

bucket = Beacon.get("bucket", namespace="aws")  # "my-bucket"
project = Beacon.get("project", namespace="gcp")  # "my-project"

# Get all non-expired values in a namespace
aws_config = Beacon.get_namespace("aws")  # {"bucket": "my-bucket"}

# List non-expired keys
keys = Beacon.list_keys()  # All non-expired keys
aws_keys = Beacon.list_keys(namespace="aws")  # Keys in namespace

# Clear operations
Beacon.unregister("api_key")  # Remove one key
Beacon.clear_namespace("aws")  # Remove all AWS keys
Beacon.clear_expired()  # Remove only expired entries
Beacon.clear()  # Remove everything

# Statistics tracking (useful for cache-like usage)
stats = Beacon.stats()  # {"hits": 10, "misses": 3, "size": 5}
Beacon.reset_stats()
```

**Automatic cleanup:** Expired entries are automatically removed when accessed via `get()` or `has()`, and when new values are registered via `register()`. Manual cleanup using `clear_expired()` is optional.

**Use cases:**
- Store permanent application configuration (no TTL)
- Cache expensive API responses (with TTL)
- Share service instances across modules without passing parameters
- Store feature flags or environment-specific settings
- Temporary session data with automatic expiration
- Access constants from anywhere without imports

**Note:** Use sparingly for truly global values. Overuse can make code harder to test and understand.

### Hash Utilities

The `Hash` class provides hashing utilities for data integrity and security:

```python
from utils import Hash

# Generate hashes (string or bytes input)
Hash.md5("hello")  # "5d41402abc4b2a76b9719d911017c592"
Hash.sha1("hello")  # SHA-1 hash
Hash.sha256("hello")  # SHA-256 hash (recommended for security)
Hash.sha512("hello")  # SHA-512 hash

# Hash files
hash_value = Hash.file("document.pdf")  # SHA-256 by default
hash_value = Hash.file("large_file.zip", algorithm="md5")

# Verify hashes
data = "important data"
hash_val = Hash.sha256(data)
is_valid = Hash.verify(data, hash_val)  # True

# HMAC for authenticated hashing
message = "secure message"
key = "secret_key"
hmac_hash = Hash.hmac_sha256(message, key)
is_valid = Hash.hmac_verify(message, key, hmac_hash)  # True

# Quick checksums for integrity
checksum = Hash.checksum("data")  # MD5 hash for quick integrity checks
```

**Use cases:**
- Verify file integrity
- Generate secure hashes for passwords (use with salt)
- HMAC for message authentication
- Checksums for data validation

**Note:** MD5 and SHA-1 are not cryptographically secure for new applications. Use SHA-256 or SHA-512 for security-sensitive operations.

### JSON Utilities

The `JSON` class provides advanced JSON operations:

```python
from utils import JSON

# Pretty printing
data = {"name": "John", "age": 30, "city": "NYC"}
print(JSON.pretty(data))
# {
#   "name": "John",
#   "age": 30,
#   "city": "NYC"
# }

print(JSON.pretty(data, indent=4))  # Custom indentation

# Minify JSON
json_str = '{"name": "John", "age": 30}'
minified = JSON.minify(json_str)  # '{"name":"John","age":30}'

# Flatten nested structures
nested = {"user": {"profile": {"name": "John", "age": 30}}}
flat = JSON.flatten(nested)
# {"user.profile.name": "John", "user.profile.age": 30}

# Unflatten back to nested
original = JSON.unflatten(flat)
# {"user": {"profile": {"name": "John", "age": 30}}}

# Custom separator
flat = JSON.flatten(nested, separator="_")
# {"user_profile_name": "John", "user_profile_age": 30}

# Safe parsing (no exceptions)
result = JSON.parse('{"valid": "json"}')  # {"valid": "json"}
result = JSON.parse('invalid json', default={})  # {}

# Validate JSON
JSON.is_valid('{"name": "John"}')  # True
JSON.is_valid('invalid')  # False

# Basic schema validation
schema = {"name": str, "age": int}
data = {"name": "John", "age": 30}
JSON.validate_schema(data, schema)  # True

# Conversion helpers
json_str = JSON.to_string(data)  # Convert to JSON string
data = JSON.from_string(json_str)  # Parse from JSON string
```

**Use cases:**
- Format JSON for display or logging
- Flatten nested API responses for analysis
- Safe JSON parsing without exception handling
- Basic data validation

### Convert Utilities

The `Convert` class provides type conversion and parsing with safe fallbacks:

```python
from utils import Convert

# Boolean conversion (handles true/false, yes/no, 1/0, on/off, enabled/disabled)
Convert.to_bool("true")  # True
Convert.to_bool("yes")  # True
Convert.to_bool("1")  # True
Convert.to_bool("off")  # False
Convert.to_bool("invalid", default=False)  # False

# Integer conversion (handles commas, decimals, strings)
Convert.to_int("123")  # 123
Convert.to_int("1,234")  # 1234
Convert.to_int("1,234.56")  # 1234 (truncates decimal)
Convert.to_int(12.8)  # 12
Convert.to_int("invalid", default=0)  # 0

# Float conversion (handles commas, strings)
Convert.to_float("123.45")  # 123.45
Convert.to_float("1,234.56")  # 1234.56
Convert.to_float(123)  # 123.0
Convert.to_float("invalid", default=0.0)  # 0.0

# Smart number conversion (int if possible, otherwise float)
Convert.to_number("123")  # 123 (int)
Convert.to_number("123.45")  # 123.45 (float)
Convert.to_number("1,234")  # 1234 (int)
Convert.to_number("123.0")  # 123 (int, not float)

# String conversion with safe None handling
Convert.to_str(123)  # "123"
Convert.to_str(None)  # ""
Convert.to_str(None, default="N/A")  # "N/A"

# Human-readable bytes to integer
Convert.bytes_from_human("1KB")  # 1024
Convert.bytes_from_human("1.5GB")  # 1610612736
Convert.bytes_from_human("500MB")  # 524288000
Convert.bytes_from_human("2 TB")  # 2199023255552

# Duration strings to seconds
Convert.duration("2h")  # 7200
Convert.duration("30m")  # 1800
Convert.duration("2h 30m")  # 9000
Convert.duration("1d 2h 30m 15s")  # 95415
Convert.duration("2.5h")  # 9000

# Safe type casting with fallback
Convert.safe_cast("123", int)  # 123
Convert.safe_cast("123.45", float)  # 123.45
Convert.safe_cast("invalid", int, default=0)  # 0
Convert.safe_cast("true", bool)  # True

# List conversion (splits strings, wraps single values)
Convert.to_list("a,b,c")  # ["a", "b", "c"]
Convert.to_list("a, b, c")  # ["a", "b", "c"] (strips whitespace)
Convert.to_list("a")  # ["a"]
Convert.to_list([1, 2, 3])  # [1, 2, 3] (unchanged)
Convert.to_list((1, 2, 3))  # [1, 2, 3] (tuple to list)
Convert.to_list("a;b;c", separator=";")  # ["a", "b", "c"]

# Dict conversion
Convert.to_dict({"a": 1})  # {"a": 1}
Convert.to_dict([("a", 1), ("b", 2)])  # {"a": 1, "b": 2}
Convert.to_dict(None, default={})  # {}
```

**Use cases:**
- Parse user input or configuration values safely
- Handle environment variables with type conversion
- Parse API responses with mixed types
- Convert human-readable sizes (1.5GB) to bytes
- Parse duration strings (2h 30m) for timeouts/delays
- Safe type coercion without exceptions

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

### Session Utilities

The `Session` class extends `requests.Session` with automatic timeout and convenient authentication:

```python
from utils import Session
from utils.session import BearerAuth, BasicAuth, APIKeyAuth, TokenAuth

# Create a session with default 30-second timeout
session = Session()

# Configure with authentication in constructor
session = Session(
    timeout=60,
    headers={"User-Agent": "MyApp/1.0"},
    auth=BearerAuth("your-token-here")
)

# Set default headers (applied to all requests)
session.set_default_header("X-Custom-Header", "value")

# Authentication options using dedicated auth classes
session.set_auth(BearerAuth("your-bearer-token"))
session.set_auth(BasicAuth("username", "password"))
session.set_auth(APIKeyAuth("your-api-key"))  # Uses X-API-Key header by default
session.set_auth(APIKeyAuth("your-key", header_name="X-Custom-Key"))
session.set_auth(TokenAuth("your-token", scheme="Token"))  # Custom scheme

# Or create custom auth class
class CustomAuth:
    def apply(self, session):
        session.set_default_header("Authorization", "Custom token")

session.set_auth(CustomAuth())

# Use all standard requests.Session methods (get, post, put, delete, etc.)
# Timeout is automatically applied to all requests
response = session.get("https://api.example.com/users")
response = session.post("https://api.example.com/users", json={"name": "Alice"})

# Convenient get_json() method that fetches and parses in one call
data = session.get_json("https://api.example.com/users/123")
users = session.get_json("https://api.example.com/users", params={"page": 1})

# Use standard response properties (from requests library)
if response.ok:  # 200-299 status codes
    print("Success!")
elif response.status_code >= 400:
    print(f"Error: {response.status_code}")

# Context manager support (inherited from requests.Session)
with Session(timeout=30, auth=BearerAuth("token123")) as session:
    data = session.get_json("https://api.example.com/data")

# Track metrics and configure retries with URL patterns
from utils.session import ExponentialRetry, LinearRetry, ConstantRetry

session = Session()

# Different retry strategies
session.add_url_pattern(
    r"/api/users",
    tag="users_api",
    retry=ExponentialRetry(attempts=3, delay=1.0, backoff=2.0)  # 1s, 2s, 4s
)
session.add_url_pattern(
    r"/api/orders/\d+",
    tag="orders_api",
    retry=LinearRetry(attempts=4, delay=1.0, backoff=1.0)  # 1s, 2s, 3s, 4s
)
session.add_url_pattern(
    r"/api/data",
    tag="data_api",
    retry=ConstantRetry(attempts=5, delay=2.0)  # 2s, 2s, 2s, 2s, 2s
)

# Make requests - metrics are tracked automatically
session.get("https://api.example.com/api/users")
session.get("https://api.example.com/api/users/123")
session.get("https://api.example.com/api/orders/456")

# View metrics
print(session.metrics)  # {"users_api": 2, "orders_api": 1}
print(session.get_metrics())  # Get a copy of metrics

# Compare metrics snapshots
snapshot = session.get_metrics()
# ... make more requests ...
session.get("https://api.example.com/api/users")
session.get("https://api.example.com/api/data")
diff = session.compare_metrics(snapshot)
print(diff)  # {"users_api": 1, "data_api": 1} - shows only changes

# Reset metrics
session.reset_metrics()

# Advanced retry strategies
from utils.session import JitterRetry, FibonacciRetry, CappedRetry, DurationRetry

# Jitter retry (prevents thundering herd)
jitter = JitterRetry(attempts=4, delay=1.0, backoff=2.0)

# Fibonacci retry (1s, 1s, 2s, 3s, 5s, 8s)
fib = FibonacciRetry(attempts=6, delay=1.0)

# Capped retry (prevent extremely long delays)
base = ExponentialRetry(attempts=10, delay=1.0, backoff=2.0)
capped = CappedRetry(base, max_delay=30.0)  # Never wait more than 30s

# Duration-based retry (keep retrying for X seconds)
duration = DurationRetry(
    duration=60.0,  # Retry for up to 60 seconds
    initial_delay=0.1,  # Start with 0.1s delay
    backoff=1.5,  # Increase delay by 1.5x each time
    max_delay=5.0  # Cap delay at 5 seconds
)
# Delays: 0.1s, 0.15s, 0.225s, 0.34s... up to 5s max, until 60s elapsed

# Automatic rate limiting (429 handling)
session = Session(
    handle_rate_limit=True,  # Default: True
    rate_limit_max_wait=60.0  # Max wait time for rate limits
)
# Session will automatically wait when it receives 429 responses
# and respect Retry-After headers
```

### JsonDB Utilities

The `JsonDB` class provides a file system-based JSON database for Pydantic models. Models are stored as JSON files in a directory structure organized by class name.

```python
from utils import JsonDB
from pydantic import BaseModel

# Define your Pydantic models
class User(BaseModel):
    id: str
    name: str
    email: str
    age: int

class Post(BaseModel):
    id: str
    title: str
    content: str
    tags: list[str]

# Create a database instance
db = JsonDB(base_path="./data")

# Save models (creates ./data/User/123.json)
user = User(id="123", name="Alice", email="alice@example.com", age=30)
db.save(user, key="123")

# Load models
loaded_user = db.load(User, key="123")
if loaded_user:
    print(f"Hello, {loaded_user.name}!")

# Check if a model exists
if db.exists(User, key="123"):
    print("User exists!")

# Update an existing model
user.age = 31
db.update(user, key="123")  # Returns True if existed, False if new

# Delete a model
db.delete(User, key="123")  # Returns True if deleted, False if not found

# List all keys for a model class
user_keys = db.list_keys(User)  # ["123", "456", "789"]

# Load all instances of a model
all_users = db.load_all(User)  # {"123": User(...), "456": User(...)}
for key, user in all_users.items():
    print(f"{key}: {user.name}")

# Clear all instances of a model class
deleted_count = db.clear(User)  # Returns number of instances deleted

# Works with nested data structures
post = Post(
    id="p1",
    title="My Post",
    content="This is a post",
    tags=["python", "database", "pydantic"]
)
db.save(post, key="p1")  # Creates ./data/Post/p1.json

# The database uses the custom JsonEncoder for serialization
# Handles datetime, sets, tuples, and objects with to_dict() methods
from datetime import datetime

class Article(BaseModel):
    id: str
    title: str
    published: datetime

article = Article(id="a1", title="News", published=datetime.now())
db.save(article, key="a1")  # Datetime is automatically serialized to ISO format

# Path structure: base_path/{ClassName}/{key}.json
# Example: ./data/User/123.json
#          ./data/Post/p1.json
#          ./data/Article/a1.json
```

## Templates

This project includes production-ready application templates that demonstrate best practices and leverage the utils package. Templates are located in the `templates/` directory.

### Falcon Server Template

A modular web server built with the Falcon framework, featuring a plugin-based architecture for easy extension.

**Quick Start**:
```bash
cd templates/falcon
pip install falcon waitress
python app.py
```

**Features**:
- Feature-based modular architecture
- Environment-based configuration
- Structured JSON logging via utils.Logger
- HTTP client integration via utils.Session
- Health check endpoint included
- Comprehensive test suite

See [templates/falcon/README.md](templates/falcon/README.md) for complete documentation.

For more information about templates, see [templates/README.md](templates/README.md).

## Features

- **Static Utility Classes**: Pure static methods with no inheritance - clean, functional API
- **17 Utility Classes**: String, Integer, Iterable, Dict, Datetime, Path, FileIO, Regex, Random, Validator, Terminal, Decorators, Logger, Encode, Decode, Session, Convert
- **String Utilities** (22 methods): Truncation, case conversions, slug generation, padding, validation (email/URL/blank), email/URL extraction, hashing
- **Integer Utilities** (15 methods): Properties (even/odd/prime), clamping, conversions (roman/words), math operations, byte formatting, percentages
- **Iterable Utilities** (22 methods): Chunking, flattening, filtering, grouping, partitioning, aggregations, sorting, finding items
- **Dict Utilities** (18 methods): Pick/omit keys, deep get/set, merging, transformations, key case conversions, flattening/unflattening
- **Datetime Utilities** (28 methods): Parsing, formatting, relative time, day/week/month/year boundaries, date arithmetic
- **Path Utilities** (12 methods): File I/O for text/lines/JSON, file management (copy/move/delete), path operations, existence checks
- **Random Utilities** (14 methods): String/number generation, choices, shuffling, UUIDs, hash generation (md5, sha1, sha256, sha512, hex)
- **Convert Utilities** (12 methods): Safe type conversion with fallbacks - to_bool, to_int, to_float, to_str, to_number, bytes_from_human, duration parsing, safe_cast, to_list, to_dict
- **Validator Utilities** (14 methods): Email, URL, phone, UUID, credit card, hex color, IPv4, empty/numeric checks, geographic validation
- **Terminal Utilities** (16 methods): Prompts (text, password, confirm, choice, select, multiline, int, float), formatting (clear, line, box, colorize, progress bar), custom validation
- **Decorator Utilities** (5 methods): Debounce, throttle, retry with backoff, memoize, once
- **Regex Utilities** (8 methods): Pattern matching, searching, replacing, splitting, group extraction, validation
- **Logger Utilities**: Structured JSON logging with thread-local context, key normalization, log searching, custom type handling
- **Encode/Decode Utilities**: Base64, URL, HTML encoding/decoding, and defang/fang for security analysis
- **Session Utilities**: Enhanced HTTP session wrapper with authentication, URL building, JSON helpers, and status checking
- **Application Templates**: Production-ready templates (Falcon server) demonstrating utils integration
- **Keyword-Only Arguments**: All parameters (except first) are keyword-only for clarity and safety
- **Type Hints**: Complete type annotations for all methods
- **Minimal Dependencies**: Only requests library required; optional dependencies include arrow for enhanced datetime parsing
- **Comprehensive Tests**: 1020+ tests covering all utilities, edge cases, and error conditions

