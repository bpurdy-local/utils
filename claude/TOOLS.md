# Project Tools

How to run development tools in this project. **Check this file first before trying to figure out tool commands.**

## Environment

```bash
# Virtual environment location
.venv/

# Activate (if needed)
source .venv/bin/activate

# Install dependencies
uv pip install -e ".[dev]"
# or
pip install -e ".[dev]"
```

## Linting (Ruff)

```bash
# Check for issues
.venv/bin/ruff check .

# Auto-fix issues
.venv/bin/ruff check --fix .

# Check specific directory
.venv/bin/ruff check utils/
```

## Formatting (Ruff)

```bash
# Format all files
.venv/bin/ruff format .

# Check formatting without changing
.venv/bin/ruff format --check .
```

## Type Checking (Pyright)

```bash
# Run type checker
.venv/bin/pyright

# Or use uvx (if pyright not in venv)
uvx pyright
```

## Testing (Pytest)

```bash
# Run all tests
.venv/bin/pytest

# Verbose output
.venv/bin/pytest -v

# Specific test file
.venv/bin/pytest tests/test_string.py

# Specific test class or method
.venv/bin/pytest tests/test_string.py::TestTruncate
.venv/bin/pytest tests/test_string.py::TestTruncate::test_truncate_shorter_than_length

# With coverage
.venv/bin/pytest --cov=utils --cov-report=html

# Show print statements
.venv/bin/pytest -s

# Stop on first failure
.venv/bin/pytest -x

# Run tests matching pattern
.venv/bin/pytest -k "truncate"
```

## Pre-commit Hooks

```bash
# Run all hooks on all files
.venv/bin/pre-commit run --all-files

# Run specific hook
.venv/bin/pre-commit run ruff --all-files

# Install hooks (first time setup)
.venv/bin/pre-commit install
```

## Common Workflows

### Before Committing
```bash
.venv/bin/ruff check --fix . && .venv/bin/ruff format . && .venv/bin/pytest
```

### Full Quality Check
```bash
.venv/bin/ruff check . && .venv/bin/ruff format --check . && .venv/bin/pyright && .venv/bin/pytest
```

## Notes

- All tools are installed in `.venv/bin/` - use full path to avoid "command not found"
- `uvx` can run tools without installing: `uvx ruff check .`
- Config is in `pyproject.toml` under `[tool.ruff]`, `[tool.pytest]`, etc.
