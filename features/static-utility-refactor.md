# Feature Plan: Static Utility Refactor and Ruff Configuration

## Summary

This is a major architectural refactoring to convert all wrapper classes from an inheritance-based approach to a static utility class pattern. Currently, wrapper classes like `String`, `Integer`, `Iterable`, `Dict`, `Datetime`, `Path`, `Regex`, `Random`, `FileIO`, `Decorators`, and `Validator` inherit from their base Python types (`str`, `int`, `list`, `dict`, `datetime`, etc.) and are used via instance methods. This refactor will transform them into pure utility classes with static methods.

The current pattern is `String("hello").truncate(5)`, which will become `String.truncate("hello", length=5)`. This change eliminates the need for backward compatibility features since this is a new library that has never been used in production.

**[Updated: 2025-11-15]** All methods will use keyword-only arguments after the first positional parameter. The first parameter is always the value being operated on (str, dict, int, etc.), and all subsequent parameters must be passed as keyword arguments using Python's `*` syntax to enforce this pattern. For example: `String.truncate(text, *, length: int, suffix: str = "...")`.

Additionally, ruff will be configured with specific rules disabled based on common annoyances and preferences.

## Acceptance Criteria

- [ ] All wrapper classes no longer inherit from base Python types
- [ ] All wrapper methods are converted to static methods that accept the value as the first parameter
- [ ] All method signatures use keyword-only arguments after the first positional parameter (using `*` syntax)
- [ ] All method signatures are updated to reflect static method pattern (e.g., `String.truncate(text: str, *, length: int, suffix: str = "...")` instead of `self.truncate(length: int, suffix: str = "...")`)
- [ ] Parameter names are descriptive and self-documenting
- [ ] All test files are updated to use the new static method calling pattern with keyword arguments
- [ ] All tests pass with the new architecture
- [ ] Ruff configuration is updated with appropriate rules disabled
- [ ] Backward compatibility references are removed from __init__.py and comments
- [ ] Redundant standalone functions are removed (only if they are pure duplicates with no additional value)
- [ ] Return types are simplified (no longer need to return wrapper instances for chaining)
- [ ] All type hints are updated to reflect the new static method signatures

## Scope/Non-Goals

### In Scope
- Convert all 11 wrapper classes to static utility classes
- Update all wrapper class method signatures to accept value as first parameter
- Enforce keyword-only arguments for all parameters after the first using the `*` separator
- Use descriptive parameter names that clearly indicate their purpose
- Update all test files to use static method calling pattern with keyword arguments
- Configure ruff with disabled rules for common annoyances
- Update CLAUDE.md documentation to reflect new architecture
- Remove all inheritance from base Python types
- Simplify return types (return plain str, int, list, etc. instead of wrapper instances)

### Non-Goals
- Adding new functionality or methods
- Performance optimization
- Adding new wrapper classes
- Changing the public API surface (method names remain the same)
- Converting standalone modules like `common.py`, `collections.py`, `misc.py`, `validation.py`, `encoding.py` to static classes (these remain as standalone function modules)
- Removing all standalone utility functions (only remove truly redundant duplicates)

## Files to Modify

### Wrapper Class Modules (Primary Changes)

1. **utils/string.py** - Convert `String(str)` to standalone class with static methods. All instance methods like `truncate(self, length: int, suffix: str = "...")` become `truncate(text: str, *, length: int, suffix: str = "...")`. The first parameter is the string value, and all other parameters must be keyword-only using the `*` separator. Use descriptive parameter names like `text` instead of `s` or `value`. Remove inheritance from `str`. Update all return types from `String` to `str` or appropriate types.

2. **utils/integer.py** - Convert `Integer(int)` to standalone class with static methods. All instance methods like `clamp(self, min_val: int, max_val: int)` become `clamp(n: int, *, min_val: int, max_val: int)`. Methods without additional parameters like `is_even(self)` become `is_even(n: int)` with no keyword-only marker needed. Remove inheritance from `int`. Update return types from `Integer` to `int`.

3. **utils/iterable.py** - Convert `Iterable(list[T])` to standalone class with static methods. Methods like `chunk(self, size: int)` become `chunk(items: list[T], *, size: int)`. Use descriptive names like `items` for the collection parameter. Remove inheritance from `list`. Update return types from `Iterable[T]` to `list[T]`.

4. **utils/dict.py** - Convert `Dict(dict[str, Any])` to standalone class with static methods. Methods like `pick(self, *keys)` become `pick(d: dict[str, Any], *keys)` where `*keys` naturally follows the first parameter. For methods with keyword arguments like `merge(self, other: dict, deep: bool = False)`, convert to `merge(d: dict[str, Any], other: dict[str, Any], *, deep: bool = False)`. Remove inheritance from `dict`. Update return types from `Dict` to `dict`.

5. **utils/datetime.py** - Convert `Datetime(datetime)` to standalone class with static methods. Complex `__new__` constructor logic will be converted to a main `parse()` static method that can handle ANY string format flexibly. Create a `format()` method that can output datetime objects in a variety of formats. Methods like `format(self, format_str: str = "%Y-%m-%d %H:%M:%S", timezone_offset: int | None = None)` become `format(dt: datetime, *, format_str: str = "%Y-%m-%d %H:%M:%S", timezone_offset: int | None = None)`. Additional convenience methods like `from_iso()`, `from_timestamp()`, `to_iso()`, `to_rfc3339()` should be included. Use descriptive parameter names. Remove inheritance from `datetime`. Update return types from `Datetime` to `datetime`.

6. **utils/path.py** - Convert to static utility class pattern. Remove inheritance from pathlib types if present. Apply keyword-only argument pattern.

7. **utils/regex.py** - Convert to static utility class pattern. Remove inheritance if present. Apply keyword-only argument pattern.

8. **utils/random_utils.py** - Already appears to be a utility module. Review and ensure consistency with static class pattern and keyword-only arguments.

9. **utils/file_io.py** - Convert to static utility class pattern if inheriting from base types. Apply keyword-only argument pattern.

10. **utils/decorators.py** - Convert to static utility class pattern if inheriting from base types. Apply keyword-only argument pattern.

11. **utils/validator.py** - Convert to static utility class pattern if inheriting from base types. Apply keyword-only argument pattern.

### Test Files (Secondary Changes)

12. **tests/test_string.py** - Update all test cases from `String("text").method(arg)` pattern to `String.method("text", arg=value)` pattern. All arguments after the first must use keyword syntax.

13. **tests/test_integer.py** - Update all test cases from `Integer(42).method(arg)` pattern to `Integer.method(42, arg=value)` pattern. Methods with only the value parameter need no keyword arguments.

14. **tests/test_iterable.py** - Update all test cases from `Iterable([...]).method(arg)` pattern to `Iterable.method([...], arg=value)` pattern with keyword arguments.

15. **tests/test_dict.py** - Update all test cases from `Dict({...}).method(arg)` pattern to `Dict.method({...}, arg=value)` pattern with keyword arguments where applicable.

16. **tests/test_datetime.py** - Update all test cases from `Datetime(...).method(arg)` pattern to `Datetime.method(datetime(...), arg=value)` pattern with keyword arguments.

17. **tests/test_path.py** - Update test patterns to use static methods with keyword arguments.

18. **tests/test_regex.py** - Update test patterns to use static methods with keyword arguments.

19. **tests/test_random_utils.py** - Review and update to use keyword arguments where applicable.

20. **tests/test_file_io.py** - Update test patterns to use static methods with keyword arguments.

### Configuration and Documentation

21. **pyproject.toml** - Update ruff configuration section to disable specific rules that are annoying or preference-based.

22. **CLAUDE.md** - Update project overview and architecture sections to reflect the new static utility class pattern with keyword-only arguments instead of inheritance-based wrappers.

23. **utils/__init__.py** - Review and simplify exports now that wrapper classes are static utility classes rather than instantiable wrappers. Remove all "backward compatibility" comments and references. Clean up the `__all__` list to reflect the new architecture.

## Design/Approach

### Current Architecture
The project currently uses an inheritance-based wrapper pattern where classes like `String` extend `str`, `Integer` extends `int`, etc. This allows for method chaining and instance-based usage like `String("hello").truncate(5).reverse()`. The wrapper instances maintain compatibility with the base types while adding utility methods.

### New Architecture
The new architecture will use static utility classes where all methods are `@staticmethod` decorated. The classes will NOT inherit from any base types. All methods will accept the value they operate on as the first positional parameter, followed by a `*` separator to enforce keyword-only arguments for all remaining parameters. For example, `String.truncate("hello", length=5)` returns a plain `str`, not a `String` instance.

### Key Design Decisions

1. **No Inheritance**: Wrapper classes will no longer inherit from base types. This simplifies the type system and makes the classes pure utilities.

2. **Static Methods**: All methods will be static methods. This is consistent with the coding standards preference for static/class methods for utility behaviors.

3. **First Parameter Pattern**: The value being operated on becomes the first positional parameter. For example, `String.truncate(text: str, *, length: int, suffix: str = "...")` instead of `self.truncate(length: int, suffix: str = "...")`.

4. **Keyword-Only Arguments**: All parameters after the first must be passed as keyword arguments. This is enforced using Python's `*` separator in the function signature. This makes method calls more readable and self-documenting. For example, `String.truncate("hello world", length=5)` is clearer than `String.truncate("hello world", 5)`.

5. **Descriptive Parameter Names**: Parameter names should be descriptive and clearly indicate their purpose. Use `text` instead of `s`, `items` instead of `lst`, `min_val` and `max_val` instead of `a` and `b`, etc.

6. **Plain Return Types**: Methods return plain Python types (`str`, `int`, `list`, `dict`, `datetime`) instead of wrapper instances. This eliminates the need for method chaining but simplifies the type system.

7. **No Backward Compatibility**: Since this is a new, unused library, no backward compatibility code is needed. We can make breaking changes freely.

### Migration Strategy

1. Start with simpler classes (`String`, `Integer`) to establish the pattern
2. Move to more complex classes (`Datetime`, `Iterable`)
3. Update tests incrementally alongside each class conversion
4. Run tests after each class conversion to catch issues early

### Ruff Configuration

The `pyproject.toml` will be updated to disable common annoying ruff rules. Common candidates include:
- Rules about line length (already set to 100)
- Rules about trailing commas
- Rules about quote styles (already set to double)
- Potentially some complexity rules if they are too strict
- Consider disabling rules about docstrings since the coding standards say not to add new docstrings

### Data Flow

Old pattern:
```
User input string -> String("hello") -> .truncate(5) -> String("hello") -> .reverse() -> String("olleh")
```

New pattern:
```
User input string -> String.truncate("hello", length=5) -> "hello" -> String.reverse("hello") -> "olleh"
```

The new pattern is more explicit and follows a functional programming style where each operation is independent rather than chained. Keyword arguments make the intent of each operation crystal clear.

## Tests to Add/Update

### Unit Tests
- All existing test files need to be updated to use the static method pattern
- No new tests are required, only updates to existing tests
- Test structure remains the same (Arrange-Act-Assert), only the calling pattern changes

### Test Update Pattern
Old:
```python
def test_truncate():
    result = String("Hello, world!").truncate(10)
    assert result == "Hello, wo..."
```

New:
```python
def test_truncate():
    result = String.truncate("Hello, world!", length=10)
    assert result == "Hello, wo..."
```

### Manual Testing Steps
1. Run full test suite after each class conversion: `pytest`
2. Run with coverage to ensure no regressions: `pytest --cov=utils --cov-report=html`
3. Test import patterns: `python -c "from utils import String; print(String.truncate('hello', length=3))"`
4. Verify type checking still passes: `uvx pyright`
5. Verify linting passes with new ruff config: `ruff check .`

## Risks & Rollback

### Risks

1. **Breaking All Existing Code**: This is a complete API change. Any code using the old pattern will break. However, since this library has never been used, this is acceptable.

2. **Type Checking Complexity**: Static methods with generic types may be more complex to type correctly, especially for classes like `Iterable[T]`.

3. **Loss of Method Chaining**: The old pattern allowed chaining like `String("hello").truncate(5).reverse()`. The new pattern requires separate calls like `String.reverse(String.truncate("hello", length=5))` or storing intermediate results. This is intentional but changes the developer experience.

**[Updated: 2025-11-15]**

4. **Keyword-Only Arguments Verbosity**: Enforcing keyword arguments may be verbose for some developers, but it significantly improves code readability and self-documentation. The slight verbosity trade-off is acceptable for clarity.

5. **Test Update Errors**: With 200+ tests to update, there's risk of introducing errors during the mass find-replace operations.

6. **Datetime Complexity**: The `Datetime` class has complex `__new__` logic for flexible parsing. Converting this to static methods will require careful design.

### Mitigation Strategies

1. **Incremental Updates**: Update one class at a time with its tests, running the test suite after each change.

2. **Type Checking**: Run `pyright` after each class conversion to catch type errors early.

3. **Git Commits**: Commit after each successful class conversion to allow easy rollback.

4. **Pattern Consistency**: Establish the pattern with simple classes first (`String`, `Integer`) before tackling complex ones (`Datetime`).

5. **Test Coverage**: Run tests with coverage report to ensure all code paths are exercised.

### Rollback Plan

If critical issues are discovered:

1. **Per-Class Rollback**: Since changes are incremental, we can rollback individual classes using git.

2. **Full Rollback**: Use `git revert` or `git reset` to return to the pre-refactor state.

3. **Hybrid Approach**: Keep some classes in the old pattern and some in the new pattern temporarily while resolving issues.

## Evidence

Files found during discovery that are relevant to this refactor:

1. `utils/string.py:4` — String class inherits from str, has 20+ instance methods
2. `utils/integer.py:4` — Integer class inherits from int, has 15+ instance methods
3. `utils/iterable.py:10` — Iterable class inherits from list[T], has 20+ instance methods
4. `utils/datetime.py:14` — Datetime class inherits from datetime, has complex __new__ method
5. `utils/dict.py:7` — Dict class inherits from dict[str, Any], has 15+ instance methods
6. `pyproject.toml:17-23` — Current ruff configuration with basic rules enabled
7. `tests/test_string.py` — Tests using String("text").method() pattern
8. `tests/test_integer.py` — Tests using Integer(n).method() pattern
9. `tests/test_iterable.py` — Tests using Iterable([...]).method() pattern
10. `CLAUDE.md:10-25` — Documents current wrapper class pattern and architecture

## Assumptions

1. **No Production Usage**: This library has never been used in production, so breaking changes are acceptable.

2. **Python 3.11+**: The project requires Python 3.11+, so we can use modern type hints and features.

3. **Test Coverage is Good**: The existing 200+ tests provide good coverage and will catch regressions during refactoring.

4. **Ruff is Preferred**: The project uses ruff for linting and formatting, and the user wants to continue using it with some rules disabled.

5. **No Performance Requirements**: The coding standards prioritize readability over performance, so the static method pattern's potential performance differences are not a concern.

6. **Method Chaining Not Required**: The loss of method chaining is acceptable since the user didn't mention it as a requirement.

7. **Keyword Arguments Acceptable**: The requirement for keyword-only arguments improves clarity and is worth the slight verbosity increase.

## Open Questions

**[Updated: 2025-11-15]** - Resolved questions 2, 4, and 6:

1. **Ruff Rules**: Will be defined later by user.

2. **Standalone Functions**: ✅ RESOLVED - Keep all standalone utility functions unless they are truly redundant. Only remove if the function is a pure duplicate of a static method with no additional value. This is the initial release, so breaking changes are acceptable and backward compatibility is not a concern.

3. **Import Pattern**: Should we change how classes are imported? Currently `from utils import String`. This still works but might be confusing since `String` is now a namespace rather than a type.

4. **Datetime Parsing and Formatting**: ✅ RESOLVED - The most critical requirements are:
   - Datetime must be able to transform ANY string to a datetime object (flexible parsing)
   - Datetime must be able to output datetime objects in a variety of formats
   - Implementation approach: Create a main `parse()` static method for string-to-datetime conversion that handles multiple formats automatically, and a `format()` method for datetime-to-string conversion with format options. Additional helper methods like `from_iso()`, `from_timestamp()` can be added as convenience methods.

5. **Validator Class**: Not clear what the current implementation looks like. Need to examine it to determine the refactoring approach.

6. **Backward Compatibility Code**: ✅ RESOLVED - Yes, remove all "backward compatibility" references from `__init__.py` and elsewhere. This is an initial release with no existing users, so backward compatibility is not needed.

## Tasks

1. Examine and document current implementation of remaining wrapper classes (Path, Regex, Random, FileIO, Decorators, Validator)

2. Update ruff configuration in pyproject.toml to disable annoying rules (need user input on specific rules)

3. Convert String class from inheritance-based to static utility class pattern with keyword-only arguments

4. Update tests/test_string.py to use static method calling pattern with keyword arguments

5. Run tests to verify String class refactor is successful

6. Convert Integer class from inheritance-based to static utility class pattern with keyword-only arguments

7. Update tests/test_integer.py to use static method calling pattern with keyword arguments

8. Run tests to verify Integer class refactor is successful

9. Convert Iterable class from inheritance-based to static utility class pattern with keyword-only arguments

10. Update tests/test_iterable.py to use static method calling pattern with keyword arguments

11. Run tests to verify Iterable class refactor is successful

12. Convert Dict class from inheritance-based to static utility class pattern with keyword-only arguments

13. Update tests/test_dict.py to use static method calling pattern with keyword arguments

14. Run tests to verify Dict class refactor is successful

15. Convert Datetime class from inheritance-based to static utility class pattern with keyword-only arguments (handle complex __new__ logic)

16. Update tests/test_datetime.py to use static method calling pattern with keyword arguments

17. Run tests to verify Datetime class refactor is successful

18. Convert Path class from inheritance-based to static utility class pattern with keyword-only arguments

19. Update tests/test_path.py to use static method calling pattern with keyword arguments

20. Run tests to verify Path class refactor is successful

21. Convert Regex class from inheritance-based to static utility class pattern with keyword-only arguments

22. Update tests/test_regex.py to use static method calling pattern with keyword arguments

23. Run tests to verify Regex class refactor is successful

24. Convert Random class from inheritance-based to static utility class pattern with keyword-only arguments

25. Update tests/test_random_utils.py to use static method calling pattern with keyword arguments

26. Run tests to verify Random class refactor is successful

27. Convert FileIO class from inheritance-based to static utility class pattern with keyword-only arguments

28. Update tests/test_file_io.py to use static method calling pattern with keyword arguments

29. Run tests to verify FileIO class refactor is successful

30. Convert Decorators class from inheritance-based to static utility class pattern with keyword-only arguments

31. Update tests for Decorators class to use static method calling pattern with keyword arguments

32. Run tests to verify Decorators class refactor is successful

33. Convert Validator class from inheritance-based to static utility class pattern with keyword-only arguments

34. Update tests for Validator class to use static method calling pattern with keyword arguments

35. Run tests to verify Validator class refactor is successful

36. Run full test suite to verify all classes work together

37. Update CLAUDE.md to document the new static utility class architecture with keyword-only arguments

38. Update utils/__init__.py exports, remove backward compatibility references and comments, and identify any truly redundant standalone functions for removal

39. Run type checking with pyright to ensure all type hints are correct

40. Run ruff linting to ensure code quality standards are met

41. Review and remove any unused code or imports introduced during refactoring

42. Create final test run with coverage report to verify complete coverage
