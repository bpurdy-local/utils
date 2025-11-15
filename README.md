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

### Standalone Functions (Backward Compatibility)

All standalone functions are still available for backward compatibility:

```python
from utils import chunk, flatten, group_by, debounce, throttle, retry, slugify

# Chunk iterables
chunk([1, 2, 3, 4, 5], 2)  # [[1, 2], [3, 4], [5]]

# Flatten nested lists
flatten([[1, 2], [3, 4]])  # [1, 2, 3, 4]

# Group by key function
group_by([1, 2, 3, 4], lambda x: x % 2)  # {0: [2, 4], 1: [1, 3]}

# Debounce function calls
@debounce(delay=0.5)
def handle_input():
    print("Input handled")

# Throttle function calls
@throttle(delay=0.5)
def handle_scroll():
    print("Scroll handled")

# Retry with exponential backoff
@retry(max_attempts=3, delay=1.0, backoff=2.0)
def unreliable_api_call():
    # Will retry up to 3 times with increasing delays
    pass

# Slugify text
slugify("Hello World!")  # "hello-world"
```

### Collection Utilities

```python
from utils import unique, first, last, pluck, pick, omit, partition, deep_get, deep_set

# Get unique items (preserves order)
unique([1, 2, 2, 3, 1])  # [1, 2, 3]
unique([{"x": 1}, {"x": 2}, {"x": 1}], key=lambda d: d["x"])  # [{'x': 1}, {'x': 2}]

# Get first/last items
first([1, 2, 3])  # 1
last([1, 2, 3])  # 3

# Extract values from list of dicts
pluck([{"name": "Alice", "age": 30}, {"name": "Bob", "age": 25}], "name")
# ['Alice', 'Bob']

# Pick/omit dictionary keys
pick({"a": 1, "b": 2, "c": 3}, "a", "c")  # {'a': 1, 'c': 3}
omit({"a": 1, "b": 2, "c": 3}, "a", "c")  # {'b': 2}

# Partition into two lists
partition([1, 2, 3, 4, 5], lambda x: x % 2 == 0)  # ([2, 4], [1, 3, 5])

# Deep get/set nested dict values
deep_get({"user": {"profile": {"name": "Alice"}}}, "user.profile.name")  # "Alice"
d = {}
deep_set(d, "user.profile.name", "Alice")  # d = {'user': {'profile': {'name': 'Alice'}}}
```

### DateTime Utilities

```python
from utils import format_date, parse_date, human_time, start_of_day, end_of_day, is_weekend

# Format dates
format_date(datetime(2024, 1, 1, 12, 0, 0))  # "2024-01-01 12:00:00"
format_date(datetime(2024, 1, 1), "%Y-%m-%d")  # "2024-01-01"

# Parse dates
parse_date("2024-01-01 12:00:00")  # datetime object

# Human-readable relative time
from datetime import timedelta
human_time(datetime.now() - timedelta(hours=2))  # "2 hours ago"

# Start/end of day
start_of_day(datetime(2024, 1, 1, 14, 30))  # datetime(2024, 1, 1, 0, 0)
end_of_day(datetime(2024, 1, 1, 14, 30))  # datetime(2024, 1, 1, 23, 59, 59, 999999)

# Check weekday/weekend
is_weekend(datetime(2024, 1, 6))  # True (Saturday)
```

### Validation Utilities

```python
from utils import is_email, is_url, is_phone, is_uuid, is_credit_card, is_empty

# Email validation
is_email("user@example.com")  # True
is_email("invalid")  # False

# URL validation
is_url("https://example.com")  # True

# Phone number validation
is_phone("+1-555-123-4567")  # True

# UUID validation
is_uuid("550e8400-e29b-41d4-a716-446655440000")  # True

# Credit card validation (Luhn algorithm)
is_credit_card("4532015112830366")  # True

# Check if empty
is_empty("")  # True
is_empty([])  # True
is_empty(None)  # True
```

### Miscellaneous Utilities

```python
from utils import generate_id, hash_string, clamp, memoize, once, bytes_to_human, percentage

# Generate random IDs
generate_id(10)  # "aB3dE5fG7h"

# Hash strings
hash_string("hello")  # "2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824"

# Clamp values
clamp(15, 0, 10)  # 10
clamp(-5, 0, 10)  # 0

# Memoize function results
@memoize
def expensive_function(x):
    return x * 2

# Call function only once
@once
def initialize():
    print("Initialized")

# Convert bytes to human-readable
bytes_to_human(1048576)  # "1.0 MB"

# Calculate percentage
percentage(25, 100)  # 25.0
percentage(1, 3, decimals=2)  # 33.33
```

## Features

- **String Wrapper**: Extended string class with 20+ utility methods
- **Common Functions**: Chunking, flattening, grouping, debouncing, throttling, retrying
- **Collection Utilities**: Unique, first/last, pluck, pick/omit, partition, deep get/set
- **DateTime Utilities**: Formatting, parsing, relative time, weekday checks
- **Validation**: Email, URL, phone, UUID, credit card, and more
- **Miscellaneous**: ID generation, hashing, clamping, memoization, and more
- **Type Hints**: Full type annotations for better IDE support
- **Standalone**: No external dependencies required

