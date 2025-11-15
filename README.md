# Utils

A Python utility library providing string wrappers and common utility functions for everyday use.

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

The project includes a comprehensive test suite with 200+ tests covering all utilities, edge cases, and error conditions.

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

The library provides wrapper classes that extend Python's built-in types with additional utility methods, similar to how `String` extends `str`.

### String Wrapper

The `String` class extends Python's built-in `str` with additional utility methods:

```python
from utils import String

# Truncate strings
text = String("This is a very long string that needs truncation")
short = text.truncate(20)  # "This is a very long..."

# Truncate by word count
text = String("Hello world from Python utils")
short = text.truncate_words(2)  # "Hello world..."

# Case conversions
String("hello world").camel_case()  # "helloWorld"
String("Hello World").snake_case()  # "hello_world"
String("Hello World").kebab_case()  # "hello-world"
String("hello world").title_case()  # "Hello World"

# String manipulation
String("hello").reverse()  # "olleh"
String("hello world").remove_whitespace()  # "helloworld"
String("hello").pad_left(10, "*")  # "*****hello"
String("hello").pad_right(10, "*")  # "hello*****"
String("hello").pad_center(10, "*")  # "**hello***"

# Prefix/suffix removal
String("prefix_hello").remove_prefix("prefix_")  # "hello"
String("hello_suffix").remove_suffix("_suffix")  # "hello"

# Text wrapping
String("This is a long line of text").wrap(10)
# ["This is a", "long line", "of text"]

# Validation
String("user@example.com").is_email()  # True
String("https://example.com").is_url()  # True

# Extraction
text = String("Contact us at info@example.com or support@example.com")
text.extract_emails()  # [String("info@example.com"), String("support@example.com")]

text = String("Visit https://example.com and https://test.com")
text.extract_urls()  # [String("https://example.com"), String("https://test.com")]
```

### Integer Wrapper

The `Integer` class extends Python's built-in `int` with additional utility methods:

```python
from utils import Integer

# Number properties
Integer(4).is_even()  # True
Integer(5).is_odd()  # True
Integer(7).is_prime()  # True

# Clamping
Integer(15).clamp(0, 10)  # 10
Integer(-5).clamp(0, 10)  # 0

# Conversions
Integer(4).to_roman()  # "IV"
Integer(123).to_words()  # "one hundred twenty-three"

# Math operations
Integer(5).factorial()  # 120
Integer(48).gcd(18)  # 6
Integer(12).lcm(18)  # 36
Integer(8).is_power_of(2)  # True

# Digit manipulation
Integer(123).digits()  # [1, 2, 3]
Integer(123).reverse()  # 321
```

### Iterable Wrapper

The `Iterable` class extends Python's `list` with additional utility methods:

```python
from utils import Iterable

# Chunking and flattening
Iterable([1, 2, 3, 4, 5]).chunk(2)  # [Iterable([1, 2]), Iterable([3, 4]), Iterable([5])]
Iterable([[1, 2], [3, 4]]).flatten()  # Iterable([1, 2, 3, 4])

# Getting items
Iterable([1, 2, 3]).first()  # 1
Iterable([1, 2, 3]).last()  # 3

# Filtering and uniqueness
Iterable([1, 2, 2, 3, 1]).unique()  # Iterable([1, 2, 3])
Iterable([1, None, 2, None, 3]).compact()  # Iterable([1, 2, 3])

# Grouping and partitioning
Iterable([1, 2, 3, 4]).group_by(lambda x: x % 2)  # {0: Iterable([2, 4]), 1: Iterable([1, 3])}
Iterable([1, 2, 3, 4, 5]).partition(lambda x: x % 2 == 0)  # (Iterable([2, 4]), Iterable([1, 3, 5]))

# Extracting from dicts
Iterable([{"name": "Alice"}, {"name": "Bob"}]).pluck("name")  # Iterable(['Alice', 'Bob'])

# Aggregations
Iterable([1, 2, 3, 4]).sum_by()  # 10
Iterable([1, 2, 3, 4]).average()  # 2.5
Iterable([1, 2, 2, 3]).count_by()  # {1: 1, 2: 2, 3: 1}

# Slicing
Iterable([1, 2, 3, 4, 5]).take(3)  # Iterable([1, 2, 3])
Iterable([1, 2, 3, 4, 5]).drop(2)  # Iterable([3, 4, 5])
```

### Datetime Wrapper

The `Datetime` class extends Python's `datetime` with additional utility methods:

```python
from utils import Datetime
from datetime import timedelta

# Formatting
dt = Datetime(2024, 1, 1, 12, 0, 0)
dt.format()  # "2024-01-01 12:00:00"
dt.format("%Y-%m-%d")  # "2024-01-01"

# Relative time
dt = Datetime.now() - timedelta(hours=2)
dt.human_time()  # "2 hours ago"

# Day boundaries
dt = Datetime(2024, 1, 1, 14, 30, 0)
dt.start_of_day()  # Datetime(2024, 1, 1, 0, 0)
dt.end_of_day()  # Datetime(2024, 1, 1, 23, 59, 59, 999999)

# Week boundaries
dt.start_of_week()  # Monday at 00:00:00
dt.end_of_week()  # Sunday at 23:59:59

# Month/Year boundaries
dt.start_of_month()  # First day of month
dt.end_of_month()  # Last day of month
dt.start_of_year()  # January 1st
dt.end_of_year()  # December 31st

# Date arithmetic
dt.add_days(5)  # Add 5 days
dt.add_hours(2)  # Add 2 hours
dt.add_weeks(1)  # Add 1 week
dt.add_months(1)  # Add 1 month
dt.add_years(1)  # Add 1 year

# Comparisons
dt.is_weekend()  # False (if weekday)
dt.is_weekday()  # True
dt.days_between(Datetime(2024, 1, 5))  # 4

# Parsing
dt = Datetime.parse("2024-01-01 12:00:00")
dt = Datetime.now()  # Current datetime
```

### Dict Wrapper

The `Dict` class extends Python's `dict` with additional utility methods:

```python
from utils import Dict

# Picking and omitting keys
d = Dict({"a": 1, "b": 2, "c": 3})
d.pick("a", "c")  # Dict({'a': 1, 'c': 3})
d.omit("a", "c")  # Dict({'b': 2})

# Deep get/set
d = Dict({"user": {"profile": {"name": "Alice"}}})
d.deep_get("user.profile.name")  # "Alice"
d.deep_set("user.profile.email", "alice@example.com")

# Merging
d1 = Dict({"a": 1, "b": {"c": 2}})
d2 = Dict({"b": {"d": 3}, "e": 4})
d1.merge(d2, deep=True)  # Deep merge nested dicts

# Transformations
d = Dict({"a": 1, "b": 2, "c": 3})
d.map_values(lambda x: x * 2)  # Dict({'a': 2, 'b': 4, 'c': 6})
d.map_keys(str.upper)  # Dict({'A': 1, 'B': 2, 'C': 3})
d.filter(lambda k, v: v > 1)  # Dict({'b': 2, 'c': 3})
d.invert()  # Dict({1: 'a', 2: 'b', 3: 'c'})

# Flattening
d = Dict({"a": {"b": {"c": 1}}})
d.flatten()  # Dict({'a.b.c': 1})
d.unflatten()  # Back to nested structure

# Utilities
d = Dict({"a": 1, "b": None, "c": 3})
d.compact()  # Dict({'a': 1, 'c': 3}) - removes None values
d.defaults({"d": 4})  # Add default values for missing keys
```

### Path Utilities

The `Path` class provides filesystem path utilities:

```python
from utils import Path

# Read and write files
path = Path("./data/file.txt")
path.write("Hello World")
content = path.read()  # "Hello World"

# Read and write lines
lines = ["line1", "line2", "line3"]
path.write_lines(lines)
content = path.read_lines()  # ["line1", "line2", "line3"]

# JSON operations
data = {"name": "Alice", "age": 30}
path.write_json(data)
content = path.read_json()  # {"name": "Alice", "age": 30}

# Path properties
path.extension()  # "txt"
path.stem()  # "file"
```

### Random Utilities

The `Random` class provides random generation utilities:

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
Random.sample([1, 2, 3, 4, 5], k=3)  # 3 random items
Random.shuffle([1, 2, 3, 4, 5])  # Shuffled list

# UUIDs
Random.uuid4()  # UUID version 4
Random.uuid1()  # UUID version 1
```

### Validator Utilities

The `Validator` class provides validation methods:

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

The `Decorators` class provides function decorators:

```python
from utils import Decorators

# Debounce function calls
@Decorators.debounce(delay=0.5)
def handle_input():
    print("Input handled")

# Throttle function calls
@Decorators.throttle(delay=0.5)
def handle_scroll():
    print("Scroll handled")

# Retry with exponential backoff
@Decorators.retry(max_attempts=3, delay=1.0, backoff=2.0)
def unreliable_api_call():
    # Will retry up to 3 times with increasing delays
    pass

# Memoize function results
@Decorators.memoize
def expensive_function(x):
    return x * 2

# Call function only once
@Decorators.once
def initialize():
    print("Initialized")
```

### Regex Utilities

The `Regex` class provides pattern matching utilities:

```python
from utils import Regex

# Match patterns
Regex.match(r"^\d+$", "123")  # True
Regex.search(r"\d+", "abc123def")  # Match object

# Find all matches
Regex.findall(r"\d+", "abc123def456")  # ["123", "456"]

# Replace patterns
Regex.sub(r"\d+", "X", "abc123def456")  # "abcXdefX"

# Split by pattern
Regex.split(r"\s+", "hello  world")  # ["hello", "world"]

# Extract groups
match = Regex.search(r"(\d+)-(\d+)", "123-456")
Regex.groups(match)  # ("123", "456")

# Validate regex
Regex.is_valid(r"^\d+$")  # True
```

### Encoding Utilities

Standalone encoding/decoding functions:

```python
from utils import (
    base64_encode,
    base64_decode,
    url_encode,
    url_decode,
    html_encode,
    html_decode,
    fang,
    defang,
)

# Base64 encoding
encoded = base64_encode("Hello World")
decoded = base64_decode(encoded)

# URL encoding
encoded = url_encode("hello world")  # "hello+world"
decoded = url_decode(encoded)

# HTML encoding
encoded = html_encode("<script>")  # "&lt;script&gt;"
decoded = html_decode(encoded)

# Fang/Defang (for security analysis)
defanged = defang("https://example.com")  # "hxxps://example[.]com"
fanged = fang("hxxps://example[.]com")  # "https://example.com"
```

## Features

- **Static Utility Classes**: Organized namespaces for String, Integer, Iterable, Dict, Datetime, Path, Regex, Random, FileIO, Decorators, and Validator
- **String Utilities**: Truncation, case conversions, manipulation, validation, and extraction
- **Integer Utilities**: Properties, clamping, conversions, math operations, and digit manipulation
- **Iterable Utilities**: Chunking, flattening, filtering, grouping, partitioning, and aggregations
- **Dict Utilities**: Pick/omit keys, deep get/set, merging, transformations, and flattening
- **Datetime Utilities**: Formatting, parsing, relative time, day/week/month boundaries, and weekday checks
- **Path Utilities**: File I/O operations for text, lines, and JSON
- **Random Utilities**: String generation, random numbers, choices, shuffling, and UUIDs
- **Validator Utilities**: Email, URL, phone, UUID, credit card, hex color, IPv4, and more
- **Decorator Utilities**: Debounce, throttle, retry, memoize, and once
- **Regex Utilities**: Pattern matching, searching, replacing, splitting, and validation
- **Encoding Utilities**: Base64, URL, HTML encoding/decoding, and fang/defang
- **Type Hints**: Full type annotations for better IDE support
- **Zero Dependencies**: No external runtime dependencies required

