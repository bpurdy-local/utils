# Code Quality Standards

Standards and patterns to check for when reviewing, debugging, or cleaning up Python code.

## Quick Reference

| Check | Good | Bad |
|-------|------|-----|
| Imports | `from typing import List` | `from typing import *` |
| Logging | `logger.error(f"Failed: {e}")` | `print(f"Error: {e}")` |
| Errors | `except ValueError as e:` | `except:` |
| Resources | `with open(f) as file:` | `file = open(f)` |
| Defaults | `def foo(*, items=None):` | `def foo(*, items=[]):` |

---

## Error Handling

### Do
```python
# Catch specific exceptions
try:
    result = process(data)
except ValueError as e:
    logger.error(f"Invalid data: {e}")
    raise
except ConnectionError as e:
    logger.warning(f"Retry needed: {e}")
    return fallback()

# Provide context in error messages
raise ValueError(f"Invalid user ID: {user_id} must be positive")

# Use context managers for resources
with open(path) as f:
    data = f.read()
```

### Don't
```python
# Bare except catches everything including KeyboardInterrupt
try:
    result = process(data)
except:
    pass

# Broad exception hiding real issues
except Exception:
    return None

# Generic error messages
raise ValueError("Invalid input")

# Resource leaks
f = open(path)
data = f.read()
# f never closed if exception occurs
```

---

## Logging

### Standards
```python
import logging

logger = logging.getLogger(__name__)  # Always use __name__

# Levels
logger.debug(f"Processing {item_id}")        # Diagnostic details
logger.info(f"Order {order_id} completed")   # Normal operations
logger.warning(f"Retry {n}/3 for {req_id}")  # Unexpected but handled
logger.error(f"Failed for {user_id}: {e}")   # Operation failed
logger.critical(f"Database down: {e}")       # App cannot continue
```

### Common Issues
```python
# BAD: print instead of logging
print(f"Debug: {value}")

# BAD: wrong level
logger.info(f"Error occurred: {e}")  # Should be logger.error

# BAD: no context
logger.error("Failed")  # Failed what? For whom?

# BAD: logging sensitive data
logger.debug(f"Login {user}:{password}")  # Never log credentials
```

---

## Documentation

### Google-style Docstrings
```python
def process_order(order_id: int, *, validate: bool = True) -> Order:
    """Process an order and return the result.

    Args:
        order_id: The unique order identifier
        validate: Whether to validate before processing

    Returns:
        The processed Order object

    Raises:
        NotFoundError: If order doesn't exist
        ValidationError: If validation fails

    Examples:
        >>> process_order(123, validate=True)
        Order(id=123, status='complete')
    """
```

### What Needs Docs
- All public functions/methods
- All classes
- Complex private functions
- Module-level docstrings for non-trivial modules

---

## Common Bugs

### Mutable Default Arguments
```python
# BUG: Default list is shared between calls
def append_to(item, target=[]):
    target.append(item)
    return target

# FIX: Use None as default
def append_to(item, target=None):
    if target is None:
        target = []
    target.append(item)
    return target
```

### Late Binding in Closures
```python
# BUG: All functions use i=4
funcs = [lambda: i for i in range(5)]

# FIX: Capture value with default argument
funcs = [lambda i=i: i for i in range(5)]
```

### String Building in Loops
```python
# SLOW: Creates new string each iteration
result = ""
for item in items:
    result += str(item)

# FAST: Join at the end
result = "".join(str(item) for item in items)
```

---

## Security Checks

### Always Verify
- [ ] No hardcoded secrets (API keys, passwords, tokens)
- [ ] No `shell=True` with user input (command injection)
- [ ] No `eval()` or `exec()` with user input
- [ ] No `pickle.load()` on untrusted data
- [ ] No `yaml.load()` without `Loader=SafeLoader`
- [ ] SQL queries use parameterization, not f-strings
- [ ] Sensitive data excluded from logs

### Patterns to Flag
```python
# Command injection risk
subprocess.run(f"ls {user_input}", shell=True)

# SQL injection risk
cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")

# Unsafe deserialization
pickle.load(untrusted_file)
yaml.load(data)  # Missing Loader
```

---

## Performance Red Flags

### O(n²) Patterns
```python
# BAD: Quadratic - checks full list each iteration
for item in items:
    if item in other_items:  # O(n) lookup
        process(item)

# GOOD: Linear - set lookup is O(1)
other_set = set(other_items)
for item in items:
    if item in other_set:
        process(item)
```

### Unnecessary Work
```python
# BAD: Recalculates on every iteration
for item in items:
    config = load_config()  # Move outside loop
    process(item, config)

# BAD: Fetches all when only need some
users = fetch_all_users()  # 10000 users
return users[:10]

# GOOD: Limit at source
users = fetch_users(limit=10)
```

---

## Testing Gaps to Check

- [ ] Edge cases: empty input, None, zero, negative
- [ ] Boundary conditions: off-by-one, max values
- [ ] Error paths: what happens when things fail?
- [ ] Concurrency: race conditions, deadlocks
- [ ] Resource cleanup: files closed, connections released

---

## Checklist for Reviews

```markdown
- [ ] Error handling is specific, not bare `except:`
- [ ] Resources use context managers (`with`)
- [ ] Logging uses logger, not print
- [ ] No sensitive data in logs or errors
- [ ] Complex logic has comments/docs
- [ ] No obvious performance issues
- [ ] Tests cover the changes
```
