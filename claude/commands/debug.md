# Debug Issue

Investigate and debug an issue in the codebase.

## Arguments
- `$DESCRIPTION`: Description of the issue or error message

## Instructions

1. **Gather Information**
   - Search for relevant code using grep/glob
   - Read the files involved in the issue
   - Check for related tests that might reveal expected behavior

2. **Reproduce the Issue**
   - Write a minimal test case that reproduces the problem
   - Run the test to confirm the issue exists

3. **Investigate**
   - Add debug output or use print statements strategically
   - Trace the data flow through the code
   - Check edge cases and boundary conditions
   - Look for common issues:
     - Type mismatches
     - Off-by-one errors
     - None/null handling
     - Empty collection handling
     - Incorrect assumptions about input

4. **Fix and Verify**
   - Make the minimal change needed to fix the issue
   - Run the reproducing test to confirm the fix
   - Run the full test suite to check for regressions
   - Remove any debug output

5. **Document**
   - Add a test case that covers this bug (if not already added)
   - Consider if similar bugs could exist elsewhere

## Common Debug Commands
```bash
# Run specific test with verbose output
pytest tests/test_file.py::TestClass::test_method -v

# Run with print statements visible
pytest -s

# Run with full traceback
pytest --tb=long

# Run tests matching a pattern
pytest -k "pattern"
```
