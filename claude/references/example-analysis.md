# Reference: Example Module Analysis

> This is an example of what a reference document should look like.
> Create these using the `/analyze` or `/architecture` commands.
> Store them here for future context in conversations.

## Overview

Brief description of what this module/system does and its purpose in the codebase.

## Key Components

### Classes
- `ClassName` - Responsibility and purpose
  - Key methods: `method1()`, `method2()`
  - Dependencies: what it relies on

### Functions
- `function_name(params)` - What it does
  - Returns: type and meaning
  - Raises: exceptions and when

## Data Flow

How data moves through this component:
1. Entry point (where data comes in)
2. Processing steps
3. Output/side effects

## Dependencies

**Internal:**
- `module.submodule` - what it provides

**External:**
- `library` - what it's used for

## Configuration

- Environment variables used
- Config files read
- Default values

## Common Patterns

Patterns used here that appear elsewhere in the codebase.

## Edge Cases

Known edge cases and how they're handled.

## Related Files

- `path/to/related.py` - relationship
- `tests/test_module.py` - test coverage

## Example Usage

```python
# How to use this component
from module import Component

result = Component.do_thing(input, option=True)
```

## Notes

- Gotchas or non-obvious behavior
- Technical debt or known issues
- Historical context if relevant

---

*Generated: YYYY-MM-DD*
*Last verified: YYYY-MM-DD*
