# Discover Project Tools

Discover how to run tools in this project and document them for future reference.

## Purpose
Figure out the correct way to run dev tools (linters, formatters, test runners, etc.) and save to `claude/TOOLS.md` so you don't have to rediscover this each session.

## Instructions

### 1. Check for Existing Documentation
First, check if `claude/TOOLS.md` already exists:
- If yes, read it and use those commands
- If no, proceed with discovery

### 2. Discovery Process

#### Check Virtual Environment
```bash
# Is there a venv?
ls -la .venv/ 2>/dev/null || ls -la venv/ 2>/dev/null

# What's installed?
.venv/bin/pip list 2>/dev/null || pip list
```

#### Check Package Manager
```bash
# Check for pyproject.toml (modern Python)
cat pyproject.toml 2>/dev/null | head -50

# Check for requirements files
ls requirements*.txt 2>/dev/null

# Check for package.json (Node)
cat package.json 2>/dev/null | head -30
```

#### Check for Tool Configs
```bash
# Ruff config
grep -A 10 "\[tool.ruff\]" pyproject.toml 2>/dev/null

# Pytest config
grep -A 10 "\[tool.pytest\]" pyproject.toml 2>/dev/null

# Pre-commit hooks
cat .pre-commit-config.yaml 2>/dev/null
```

### 3. Test Commands
Try commands in order of likelihood:

**Python/Ruff:**
```bash
# Try these in order until one works
.venv/bin/ruff check .
ruff check .
uvx ruff check .
python -m ruff check .
```

**Pytest:**
```bash
.venv/bin/pytest
pytest
python -m pytest
```

**Type Checking:**
```bash
.venv/bin/pyright
uvx pyright
npx pyright
mypy .
```

### 4. Document What Works

Create/update `claude/TOOLS.md` with working commands:

```markdown
# Project Tools

## Environment Setup
```bash
# Activate virtual environment
source .venv/bin/activate

# Install dependencies
uv pip install -e ".[dev]"
```

## Linting
```bash
# Check for issues
.venv/bin/ruff check .

# Auto-fix issues
.venv/bin/ruff check --fix .
```

## Formatting
```bash
.venv/bin/ruff format .
```

## Type Checking
```bash
uvx pyright
```

## Testing
```bash
# All tests
.venv/bin/pytest

# Specific file
.venv/bin/pytest tests/test_file.py

# With coverage
.venv/bin/pytest --cov=utils
```

## Pre-commit
```bash
pre-commit run --all-files
```
```

### 5. Verify and Save
- Run each command to verify it works
- Note any special flags or options needed
- Save to `claude/TOOLS.md`

**IMPORTANT:** Always check `claude/TOOLS.md` first in future sessions before trying to figure out how to run tools.
