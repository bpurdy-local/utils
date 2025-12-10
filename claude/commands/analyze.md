# Analyze Code

Analyze code and create a reference document for future questions.

## Arguments
- `$TARGET`: What to analyze (e.g., "utils/string.py", "authentication flow", "API endpoints")

## Instructions

### 1. Gather Information
- Read all relevant source files
- Identify key classes, functions, and their relationships
- Note dependencies (imports, external libraries)
- Find related tests to understand expected behavior

### 2. Create Reference Document

Output a structured analysis to `claude/references/$TARGET.md`:

```markdown
# Reference: $TARGET

## Overview
Brief description of what this code does and its purpose.

## Key Components

### Classes
- `ClassName` - Purpose and responsibility
  - Key methods: `method1()`, `method2()`
  - Dependencies: what it relies on

### Functions
- `function_name(params)` - What it does
  - Returns: return type and meaning
  - Raises: exceptions and when

## Data Flow
How data moves through this code:
1. Entry point
2. Processing steps
3. Output/side effects

## Dependencies
- Internal: other modules in this project
- External: third-party libraries

## Configuration
Any config files, environment variables, or settings.

## Common Patterns
Patterns used in this code that appear elsewhere.

## Edge Cases
Known edge cases and how they're handled.

## Related Files
- `path/to/related.py` - relationship
- `tests/test_file.py` - test coverage

## Example Usage
```python
# How to use this code
```

## Notes
Any gotchas, technical debt, or important context.
```

### 3. Save Reference
Save the analysis to `claude/references/` for future use:
- Use descriptive filenames: `string-utilities.md`, `auth-flow.md`
- Update if the code changes significantly

### 4. When to Create References
Good candidates for reference docs:
- Complex subsystems with many moving parts
- Code you'll need to modify or extend later
- Areas with non-obvious behavior
- Integration points with external systems
- Frequently asked about code
