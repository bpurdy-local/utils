# Normalize Code Standards

Scan the codebase and normalize documentation, logging, and code style for consistency.

## Arguments
- `$SCOPE`: What to normalize (e.g., "all", "src/", "module_name")
- `$FOCUS`: Optional focus area ("docs", "logging", "all")

## Instructions

### 1. Discover Current State

Scan the codebase to understand current patterns:

```bash
# Documentation patterns
grep -rn '"""' --include="*.py" $SCOPE | head -20

# Logging patterns
grep -rn "print(\|logger\.\|logging\." --include="*.py" $SCOPE

# Find inconsistencies
grep -rn "getLogger" --include="*.py" $SCOPE
```

### 2. Audit & Report

Generate a comprehensive report:

```markdown
## Normalization Audit: $SCOPE

### Documentation Issues
| File | Issue |
|------|-------|
| path/file.py | Missing module docstring |
| path/file.py:ClassName | Incomplete Args section |
| path/file.py:func | NumPy style (should be Google) |

### Logging Issues
| File:Line | Issue | Fix |
|-----------|-------|-----|
| path/file.py:42 | print() statement | Convert to logger.info() |
| path/file.py:87 | logger.info for error | Change to logger.error() |
| path/auth.py:30 | Logs password | Remove sensitive data |

### Style Inconsistencies
| Issue | Files Affected |
|-------|----------------|
| Mixed quote styles | file1.py, file2.py |
| Inconsistent naming | auth.py (camelCase), user.py (snake_case) |
```

---

## Documentation Standards

### Module Docstrings
```python
"""Brief module description.

Longer description explaining what this module provides
and any important usage notes.
"""
```

### Function/Method Docstrings (Google style)
```python
def function_name(param1: str, *, param2: int = 10) -> bool:
    """Brief one-line description.

    Longer description if needed.

    Args:
        param1: Description of param1
        param2: Description of param2

    Returns:
        Description of return value

    Raises:
        ValueError: When param1 is empty

    Examples:
        >>> function_name("test", param2=5)
        True
    """
```

### Common Doc Fixes
- Add missing module docstrings
- Convert NumPy/Sphinx style to Google style
- Add missing Args/Returns sections
- Remove outdated parameter documentation
- Fix examples that don't match actual output

---

## Logging Standards

### Logger Initialization
```python
import logging

logger = logging.getLogger(__name__)  # Always use __name__
```

### Log Levels
| Level | Use For |
|-------|---------|
| DEBUG | Diagnostic details, variable values |
| INFO | Normal operations, startup/shutdown |
| WARNING | Unexpected but handled situations |
| ERROR | Operation failed, exception caught |
| CRITICAL | App cannot continue |

### Message Format
```python
# Good - includes context
logger.info(f"Processing order {order_id} for user {user_id}")
logger.error(f"Failed to fetch user {user_id}: {e}", exc_info=True)

# Bad - no context
logger.info("Processing")
logger.error("Failed")
```

### Common Logging Fixes
- Convert `print()` to appropriate logger calls
- Fix wrong log levels (info for errors, etc.)
- Remove sensitive data (passwords, tokens, PII)
- Add context to generic messages
- Standardize logger naming to `__name__`

---

## Normalization Process

1. **Review the audit report**
2. **Prioritize fixes:**
   - Critical: Security issues (logged secrets)
   - High: Missing error handling logs
   - Medium: Documentation gaps
   - Low: Style inconsistencies
3. **Make changes incrementally** - one file at a time
4. **Verify after each change** - run tests
5. **Save standards** to `claude/references/code-standards.md`

## Output

After normalization, save discovered standards to references:
- `claude/references/code-standards.md` - Project conventions
- Update `claude/TOOLS.md` if new linting rules added
