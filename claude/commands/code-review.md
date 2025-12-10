# Code Review

Perform a thorough code review to identify bugs, issues, and improvements.

## Arguments
- `$TARGET`: File, directory, or PR to review (e.g., "src/auth/", "PR #123", "recent changes")

## Instructions

### 1. Gather Context
- Read the code to be reviewed
- Understand what it's supposed to do
- Check for related tests
- Look at recent changes if reviewing a PR

### 2. Review Checklist

#### Correctness
- [ ] Logic is correct and handles all cases
- [ ] Edge cases handled (empty, null, boundaries)
- [ ] Error handling is appropriate
- [ ] No off-by-one errors
- [ ] No race conditions or concurrency issues
- [ ] Return values are correct

#### Security
- [ ] No hardcoded secrets or credentials
- [ ] Input is validated/sanitized
- [ ] No SQL injection vulnerabilities
- [ ] No command injection (shell=True, eval, exec)
- [ ] No unsafe deserialization
- [ ] Sensitive data not logged

#### Performance
- [ ] No obvious O(n²) or worse on large data
- [ ] No unnecessary allocations in loops
- [ ] Resources are properly closed/released
- [ ] No memory leaks (growing caches, unclosed handles)

#### Maintainability
- [ ] Code is readable and self-documenting
- [ ] Functions/methods are focused (single responsibility)
- [ ] No dead code or commented-out code
- [ ] No TODOs that should be addressed now
- [ ] Consistent naming conventions

#### Testing
- [ ] Tests exist for new/changed code
- [ ] Tests cover edge cases
- [ ] Tests are meaningful (not just for coverage)

### 3. Output Format

Provide findings in this format:

```markdown
## Code Review: $TARGET

### Summary
Brief overview of what was reviewed and overall assessment.

### Critical Issues (must fix)
- **[File:Line]** Description of issue
  - Why it's a problem
  - Suggested fix

### Warnings (should fix)
- **[File:Line]** Description of issue
  - Impact
  - Suggested fix

### Suggestions (nice to have)
- **[File:Line]** Description of improvement
  - Benefit

### Positive Notes
- Things done well worth highlighting
```

### 4. Common Issues to Look For

**Python-specific:**
- Mutable default arguments (`def foo(items=[]`)
- Not using context managers for resources
- Catching too broad exceptions (`except:` or `except Exception:`)
- String concatenation in loops (use join)
- Not using f-strings for formatting

**General:**
- Magic numbers without explanation
- Deeply nested conditionals
- Functions doing too many things
- Inconsistent error handling patterns
- Missing type hints or wrong types

### 5. Save Reference (Optional)

If significant findings, save to `claude/references/reviews/` for future reference:
- `claude/references/reviews/YYYY-MM-DD-module-name.md`
