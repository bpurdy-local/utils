# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python utility library that provides static utility classes for common operations on built-in Python types. The library follows a functional approach with organized namespaces:

1. **Static Utility Classes**: Type-safe utility classes (`String`, `Integer`, `Iterable`, `Datetime`, `Dict`, `Path`, `Regex`, `Random`, `FileIO`, `Decorators`, `Validator`) that provide static methods for working with their respective types
2. **Standalone Functions**: Backward-compatible functions for common operations

All utility classes use static methods that accept the value to operate on as the first positional parameter, followed by keyword-only arguments (enforced with the `*` separator). This design provides clear, consistent APIs without the overhead of instantiation or inheritance.

Example:
```python
from utils import String

# Static method API with keyword-only arguments
result = String.truncate("Hello World", length=5, suffix="...")  # "Hello..."
```

## Development Setup

Install in editable mode with development dependencies:

```bash
# Using uv (preferred)
uv pip install -e ".[dev]"

# Or using pip
pip install -e ".[dev]"
```

The virtual environment is at `.venv/` and should be activated before development.

## Testing

Run tests using pytest:

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=utils --cov-report=html

# Run specific test file
pytest tests/test_string.py

# Run specific test
pytest tests/test_string.py::test_truncate

# Exclude slow tests
pytest -m "not slow"

# Verbose output
pytest -v
```

The test suite has 200+ tests covering all utilities, edge cases, and error conditions. Tests are organized in the `tests/` directory with one test file per module.

## Code Quality

### Linting and Formatting

```bash
# Run ruff linter (auto-fix)
ruff check --fix .

# Format code with ruff
ruff format .

# Type checking with pyright
uvx pyright

# JavaScript/TypeScript linting (minimal JS tooling present)
npm run lint
npm run format
npm run typecheck
```

### Pre-commit Hooks

The project uses pre-commit hooks configured in `.pre-commit-config.yaml`:
- Ruff linting and formatting
- Pyright type checking

Install hooks with:
```bash
pre-commit install
```

## Architecture

### Module Organization

Each utility class lives in its own module under `utils/`:

- `string.py` - String utility class with text manipulation methods
- `integer.py` - Integer utility class with number utilities
- `iterable.py` - Iterable utility class with collection operations
- `datetime.py` - Datetime utility class with date/time utilities
- `dict.py` - Dict utility class with dictionary operations
- `path.py` - Path utility class for filesystem operations
- `regex.py` - Regex utility class for pattern matching
- `random_utils.py` - Random number/selection utilities
- `file_io.py` - File I/O operations
- `decorators.py` - Function decorators
- `validator.py` - Validation utility class

Standalone utility modules:
- `common.py` - Common functions (chunk, flatten, debounce, throttle, retry, slugify)
- `collections.py` - Collection utilities (unique, first/last, pluck, pick/omit, partition)
- `misc.py` - Miscellaneous utilities (clamp, memoize, once, generate_id, hash_string, bytes_to_human)
- `validation.py` - Validation functions (is_email, is_url, is_phone, etc.)
- `encoding.py` - Encoding/decoding utilities (base64, URL, HTML, fang/defang)

### Static Utility Class Pattern

All utility classes follow this pattern:

1. Define as a regular class (no inheritance from base types)
2. Implement static methods using `@staticmethod` decorator
3. First parameter accepts the value to operate on
4. Use `*` separator to enforce keyword-only arguments for all other parameters
5. Provide comprehensive type hints for all parameters and return values
6. Return the appropriate Python built-in type (not a wrapper instance)
7. Handle edge cases gracefully (empty inputs, None values, invalid types)

Example from `String`:
```python
class String:
    @staticmethod
    def truncate(text: str, *, length: int, suffix: str = "...") -> str:
        """Truncate text to specified length, adding suffix if truncated.

        Args:
            text: The string to truncate
            length: Maximum length (keyword-only)
            suffix: String to append if truncated (keyword-only, default "...")

        Returns:
            Truncated string with suffix if needed
        """
        if len(text) <= length:
            return text
        return text[:length - len(suffix)] + suffix
```

Key principles:
- **Static methods only**: No instance methods, no `__init__`, no inheritance
- **Keyword-only arguments**: All parameters after the first use `*` separator
- **Clear function signatures**: Explicit parameter names improve readability
- **Type safety**: Complete type hints for IDE support and type checking
- **Consistent API**: All utility classes follow the same calling convention

### Public API

All public exports are defined in `utils/__init__.py` via the `__all__` list. When adding new functionality:

1. Create/update the appropriate module
2. Add exports to `__init__.py`
3. Update `__all__` list
4. Add comprehensive tests
5. Update README.md with usage examples

## Configuration

### Python Config (`pyproject.toml`)

- **Python Version**: Requires Python 3.11+
- **No Runtime Dependencies**: The library has zero external dependencies
- **Optional Dependencies**:
  - `dev` - pytest, pytest-cov
  - `datetime` - arrow (for enhanced datetime support)
- **Ruff**: Line length 100, Python 3.11 target
- **Pyright**: Standard type checking mode

### TypeScript Config (`tsconfig.json`)

Minimal TypeScript configuration exists for potential JS/TS utilities. Currently unused but configured with:
- Target: ES2022
- Module: ESNext
- Strict mode enabled

## Adding New Utilities

When adding new utility classes or utilities:

1. Create the module in `utils/`
2. Write comprehensive tests in `tests/test_<module>.py`
3. Update `utils/__init__.py` to export the new functionality
4. Update README.md with usage examples
5. Ensure type hints are complete
6. Run tests and type checking before committing

For utility classes:
- Use static methods with `@staticmethod` decorator
- First parameter is the value to operate on
- All other parameters must be keyword-only (use `*` separator)
- Return standard Python types (str, int, list, dict, etc.)
- Handle edge cases (empty inputs, None values, invalid types)
- Maintain consistency with existing utility class patterns
- Do NOT inherit from base types
- Do NOT implement instance methods or constructors

Example pattern:
```python
class MyUtility:
    @staticmethod
    def my_method(value: SomeType, *, param1: Type1, param2: Type2 = default) -> ReturnType:
        """Method description.

        Args:
            value: The value to operate on
            param1: Description (keyword-only)
            param2: Description (keyword-only, default value)

        Returns:
            Description of return value
        """
        # Implementation
        pass
```

For standalone functions:
- Use type hints for parameters and return values
- Handle edge cases gracefully
- Consider adding equivalent static methods to relevant utility classes
