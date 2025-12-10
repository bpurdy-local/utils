# Code Cleanup

Identify and clean up dead code, unused imports, and technical debt.

## Arguments
- `$SCOPE`: What to clean (e.g., "all", "src/", "module_name")

## Instructions

### 1. Identify Issues

Scan for common cleanup targets:

```bash
# Unused imports (if ruff/flake8 available)
ruff check --select=F401 $SCOPE

# TODO/FIXME/HACK comments
grep -rn "TODO\|FIXME\|HACK\|XXX" --include="*.py" $SCOPE

# Commented-out code
grep -rn "^[[:space:]]*#.*def \|^[[:space:]]*#.*class \|^[[:space:]]*#.*import " --include="*.py" $SCOPE

# Print statements (usually debug leftovers)
grep -rn "print(" --include="*.py" $SCOPE | grep -v "test_"

# Debugger statements
grep -rn "breakpoint()\|pdb\|ipdb" --include="*.py" $SCOPE

# Empty files
find $SCOPE -name "*.py" -empty

# Duplicate code (manual review needed)
```

### 2. Generate Cleanup Report

```markdown
## Cleanup Audit: $SCOPE

### Dead Code
| File | Line | Issue |
|------|------|-------|
| path/file.py | 42-55 | Commented-out function |
| path/old.py | entire | File appears unused |

### Unused Imports
| File | Import |
|------|--------|
| path/file.py | from os import unused_func |
| path/utils.py | import never_used |

### Debug Leftovers
| File:Line | Issue |
|-----------|-------|
| path/file.py:87 | print(f"DEBUG: {value}") |
| path/api.py:123 | breakpoint() |

### TODOs to Address or Remove
| File:Line | Comment | Action |
|-----------|---------|--------|
| path/file.py:30 | # TODO: optimize this | Address or create ticket |
| path/old.py:15 | # FIXME: broken | Fix or remove |
| path/file.py:99 | # TODO from 2019 | Likely stale, remove |

### Other Issues
| File | Issue |
|------|-------|
| path/file.py | Multiple blank lines (style) |
| path/utils.py | Unreachable code after return |
```

### 3. Cleanup Priorities

**Immediate (do now):**
- Debug statements (breakpoint, pdb)
- Print statements in non-test code
- Unused imports

**Soon (with approval):**
- Commented-out code blocks
- Dead/unreachable code
- Empty files

**Review needed:**
- TODOs - decide: fix, create ticket, or remove
- Potentially unused functions/classes (need to verify)

### 4. Safe Cleanup Process

For each cleanup:

1. **Verify it's safe to remove**
   - Check for usages: `grep -rn "function_name" .`
   - Check if exported in `__init__.py`
   - Check if referenced in tests

2. **Make the change**

3. **Verify nothing broke**
   - Run tests
   - Run type checker
   - Quick smoke test if applicable

### 5. Common Cleanup Patterns

**Remove unused imports:**
```python
# Before
import os
import sys  # unused
from typing import List, Dict, Optional  # Dict unused

# After
import os
from typing import List, Optional
```

**Remove commented code:**
```python
# Before
def active_function():
    pass

# def old_function():
#     """This was replaced."""
#     return "old"

# After
def active_function():
    pass
```

**Handle TODOs:**
```python
# If still relevant, create a ticket and reference it:
# TODO(JIRA-123): Optimize this query for large datasets

# If stale/done, remove entirely
```

### 6. Save Findings

If significant technical debt found, save to `claude/references/technical-debt.md`:

```markdown
# Technical Debt Inventory

## High Priority
- [ ] path/module.py - Needs refactoring (reason)

## Medium Priority
- [ ] Unused code in path/old.py - verify and remove

## Low Priority / Future
- [ ] Style inconsistencies in path/
```
