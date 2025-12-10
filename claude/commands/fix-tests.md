# Fix Failing Tests

Debug and fix failing tests in the test suite.

## Arguments
- `$TEST_PATH`: Optional path to specific test file or test (e.g., "tests/test_string.py::TestTruncate")

## Instructions

### 1. Identify Failing Tests
```bash
# Run all tests and see failures
pytest --tb=short

# Run specific test file
pytest tests/test_file.py -v

# Run tests matching a pattern
pytest -k "test_name_pattern" -v

# Stop on first failure
pytest -x
```

### 2. Get Detailed Failure Info
```bash
# Full traceback
pytest tests/test_file.py --tb=long

# Show local variables in traceback
pytest tests/test_file.py --tb=long -l

# Show print statements
pytest tests/test_file.py -s

# Combined verbose output
pytest tests/test_file.py -v -s --tb=long
```

### 3. Common Failure Patterns

**AssertionError**
- Check expected vs actual values
- Verify test data is correct
- Check for off-by-one errors

**ImportError**
- Module not exported in `__init__.py`
- Circular import
- Missing dependency

**TypeError**
- Wrong number of arguments
- Wrong argument types
- Missing keyword-only argument

**AttributeError**
- Method doesn't exist
- Typo in method name
- Wrong class being used

**KeyError / IndexError**
- Empty collection not handled
- Missing key in dict
- Out of bounds access

### 4. Debugging Strategies
```python
# Add debug output in test
def test_something():
    result = function_under_test(input)
    print(f"DEBUG: result = {result}")  # pytest -s to see
    assert result == expected

# Use breakpoint for interactive debugging
def test_something():
    result = function_under_test(input)
    breakpoint()  # Drops into pdb
    assert result == expected
```

### 5. Fix and Verify
1. Make the fix (either in source or test)
2. Run the specific failing test
3. Run related tests in the same file
4. Run full test suite to check for regressions

### 6. Test Isolation Issues
If tests pass individually but fail together:
- Check for shared mutable state
- Check for file system side effects
- Use fixtures for setup/teardown
- Run with `pytest --randomly-seed=<seed>` to reproduce order
