# Feature Plan: Pydantic Utility Classes

**[Updated: 2025-01-20]** - Removed "Pydantic" prefix from class and file names since they're already under `utils/pydantic/` directory

**[Updated: 2025-01-20]** - Changed Types class approach: instead of providing standard transforms, allow users to pass in one or more transform functions (like String.truncate) that will be applied

## Summary

Add a new `utils/pydantic/` directory containing Pydantic 2-specific utility classes that follow the same static utility class pattern as existing utils. This feature will provide two main utility classes:

1. **Validator** - Common Pydantic validators for field-level validation
2. **Types** - Factory methods that create custom field types by wrapping user-provided transform functions

This extends the existing utility library to better support Pydantic model development, providing reusable validators and a flexible way to apply transformations to model fields. The utilities will complement the existing `Validator` class (which provides standalone validation functions) and integrate seamlessly with Pydantic 2's validation system.

**Problem it solves:**
- Eliminates duplicate validator code across Pydantic models
- Provides flexible way to apply transformations from existing utils (String, Integer, etc.) to Pydantic fields
- Offers reusable, tested validators following the library's static utility pattern
- Makes Pydantic model definitions more concise and maintainable
- Allows composition of multiple transforms on a single field

**Why needed:**
- Pydantic is already a core dependency (used by JsonDB)
- Common validators are frequently needed across models
- Users want to apply existing utility transforms (String.strip, String.slug, etc.) to Pydantic fields
- Current approach requires writing custom validators inline or copying code
- Centralizes Pydantic-specific utilities in one discoverable location

## Acceptance Criteria

- [ ] New `utils/pydantic/` directory created with proper structure
- [ ] `Validator` class implemented with static methods returning Pydantic validators
- [ ] `Types` class implemented with factory methods that accept transform functions
- [ ] Types.transform() method accepts single transform function or list of transforms
- [ ] All utility classes follow the existing static utility pattern (static methods, keyword-only args after first param)
- [ ] Comprehensive test coverage covering all validators and type factories
- [ ] Classes exported from `utils/__init__.py` and appear in `__all__`
- [ ] Classes exported with descriptive names to avoid conflicts (e.g., `PydanticValidator`, `PydanticTypes`)
- [ ] Documentation updated in README.md with usage examples showing transform composition
- [ ] CLAUDE.md updated to include new Pydantic utilities
- [ ] All tests pass including new Pydantic utility tests
- [ ] Linting passes (ruff check, ruff format, pyright)
- [ ] Works with Pydantic 2.x (already a project dependency)

## Scope/Non-Goals

### In Scope

- Static utility class for common Pydantic field validators
- Static utility class for creating custom field types from user-provided transform functions
- Common validators: email format, URL format, phone validation, string constraints, numeric ranges, list constraints
- Type factory that wraps one or more transform functions into Pydantic-compatible types
- Support for chaining multiple transforms (e.g., strip then lowercase then slug)
- Integration with existing utils by allowing users to pass any utility method as a transform
- Comprehensive test suite with edge cases
- Documentation and examples showing how to use existing utils with Types
- Package structure following existing patterns (`utils/pydantic/__init__.py`)

### Non-Goals

- Pre-built transform types (users compose their own from existing utils)
- Custom Pydantic BaseModel subclasses (users define their own models)
- Database integration beyond what JsonDB already provides
- Schema generation utilities (Pydantic handles this)
- Migration utilities for Pydantic v1 to v2
- FastAPI-specific integrations (out of scope for this library)
- Async validators or transforms (focus on synchronous first)
- Complex cross-field validation (Pydantic's model validators handle this better)

## Files to Modify

### New Files

1. **`utils/pydantic/__init__.py`**
   - Package initialization file
   - Exports Validator and Types classes
   - Includes __all__ list with "Validator" and "Types"

2. **`utils/pydantic/validator.py`**
   - Validator static utility class
   - Methods return Pydantic field validators (callables)
   - Example methods: email validator, phone validator, url validator, min/max length, regex pattern, choices validator
   - Each method follows pattern: static method takes config parameters as keyword args, returns a validator function
   - Uses Pydantic 2 validation approach (field_validator, AfterValidator, BeforeValidator)

3. **`utils/pydantic/types.py`**
   - Types static utility class
   - Factory methods that accept user-provided transform functions
   - Main method: transform() accepts single function or list of functions, returns Annotated type
   - Transforms are applied in order using BeforeValidator
   - Each method returns an Annotated type that can be used directly in model field definitions
   - Handles None values appropriately (skip transform or propagate based on config)

4. **`tests/test_pydantic_validator.py`**
   - Comprehensive test suite for pydantic Validator class
   - Tests each validator with valid and invalid inputs
   - Tests edge cases and boundary conditions
   - Uses Pydantic models to test validators in real scenarios

5. **`tests/test_pydantic_types.py`**
   - Comprehensive test suite for pydantic Types class
   - Tests transform factory with single and multiple transforms
   - Tests composition of transforms from existing utils (String.strip, String.slug, etc.)
   - Tests type hints work correctly in model definitions
   - Verifies transforms are applied in correct order
   - Tests None handling
   - Tests with Field() constraints

### Modified Files

1. **`utils/__init__.py`**
   - Add imports for pydantic Validator and Types with aliased names to avoid conflicts
   - Import as: `from utils.pydantic import Validator as PydanticValidator, Types as PydanticTypes`
   - Add both aliased classes to __all__ list under new comment section "# Pydantic Utility Classes"
   - Export as "PydanticValidator" and "PydanticTypes" to distinguish from the standalone Validator class

2. **`README.md`**
   - Add new section "Pydantic Utilities" after Validator section
   - Include usage examples for both PydanticValidator and PydanticTypes
   - Show how to use validators in Pydantic models
   - Show how to create custom types by passing transform functions
   - Show examples of chaining transforms (strip then slug, lowercase then truncate, etc.)
   - Demonstrate using existing utility methods as transforms
   - Update feature count and test count in Features section

3. **`CLAUDE.md`**
   - Add PydanticValidator and PydanticTypes to Available Utility Classes list
   - Add utils/pydantic/ to Module Organization section
   - Document that these classes integrate with Pydantic 2 validation system
   - Note that Pydantic is already a core dependency
   - Clarify that internally the classes are named Validator and Types, but exported with Pydantic prefix
   - Document that Types accepts user-provided transform functions rather than providing pre-built transforms

## Design/Approach

### Architecture Integration

The new Pydantic utilities fit into the existing architecture as a specialized domain package, similar to how `utils/db/json/` handles database operations. The package structure will be:

```
utils/
  pydantic/
    __init__.py      # Exports Validator, Types
    validator.py     # Validator factory methods
    types.py         # Transform wrapper factory methods
```

### Static Utility Pattern

Following the existing pattern, both classes will be static utility classes:

**Validator Pattern:**
- Each method is a factory that returns a validator function
- Parameters use keyword-only args after the required config
- Example: `Validator.min_length(*, length: int) -> Callable` returns a validator that checks minimum length
- Returned validators are compatible with Pydantic's `field_validator` decorator or `Field(validators=[...])`

**Types Pattern:**
- Factory methods that accept user-provided transform functions
- Main method: `Types.transform(transform, *, skip_none: bool = True)` or `Types.transform(transforms, *, skip_none: bool = True)` for multiple
- Accepts single callable or list of callables
- Returns Annotated type with BeforeValidator that applies transforms in sequence
- Example: `Types.transform(String.strip)` creates a type that strips whitespace
- Example: `Types.transform([String.strip, String.lower, String.slug])` chains multiple transforms
- Can be used directly as field type hints: `name: PydanticTypes.transform(String.strip)`

### Key Design Decisions

1. **User-Provided Transforms**: Instead of pre-built transforms, accept any callable that transforms a value
2. **Transform Chaining**: Support lists of transforms that are applied in order
3. **Static Factory Pattern**: Methods return validators/types rather than being validators themselves, allowing configuration
4. **Pydantic 2 Native**: Use Pydantic 2's Annotated types and validator approach (not v1 compatibility)
5. **Leverage Existing Utils**: Users pass existing utility methods (String.slug, String.strip, etc.) as transforms
6. **Composable**: Multiple transforms can be chained together
7. **No Magic**: Clear, explicit behavior - transformations happen before validation, validators check after
8. **Naming Strategy**: Classes named simply (Validator, Types) within the pydantic package, but exported with "Pydantic" prefix to avoid confusion with the standalone Validator class

### Data Flow

**For Validators:**
User defines Pydantic model → Uses PydanticValidator method in field definition → Pydantic applies validator during instantiation → Value validated or ValidationError raised

**For Custom Types with Transforms:**
User defines Pydantic model → Uses PydanticTypes.transform() with utility methods as field type → Pydantic instantiation applies transforms in order then validates → Transformed value assigned or ValidationError raised

**Transform Chain Example:**
```
Input: "  Hello World!  "
↓ String.strip
"Hello World!"
↓ String.lower
"hello world!"
↓ String.slug
"hello-world"
```

### Integration with Existing Utils

- Users pass String.strip, String.slug, String.truncate, etc. as transforms
- Users pass Integer.clamp, Integer.to_words, etc. as transforms
- pydantic Validator can use utils.Validator.email() internally for email validation
- pydantic Validator can use Regex.match() for pattern validation
- Types.transform() creates wrapper that applies any existing utility method

This creates a cohesive utility ecosystem where Pydantic types are built by composing existing utility functions.

## Tests to Add/Update

### New Test Files

**tests/test_pydantic_validator.py** (estimated 40+ tests):
- Test email validator with valid/invalid emails
- Test phone validator with various formats
- Test URL validator with valid/invalid URLs
- Test min/max length validators with boundaries
- Test numeric range validators
- Test regex pattern validator
- Test choices validator with valid/invalid choices
- Test validators integrated into Pydantic models
- Test validator error messages
- Test validator with None values (optional fields)
- Test validator composition (multiple validators on one field)

**tests/test_pydantic_types.py** (estimated 35+ tests):
- Test transform with single function (String.strip)
- Test transform with multiple functions in chain
- Test transform with String utils (strip, lower, upper, slug, truncate)
- Test transform with Integer utils (clamp, abs)
- Test transform with custom user functions
- Test transforms in Pydantic model definitions
- Test transformation order is preserved
- Test type hints work correctly with IDE/type checkers
- Test optional fields with skip_none=True
- Test optional fields with skip_none=False
- Test transform with default values
- Test transform with Field() constraints
- Test transform error handling (when transform raises exception)
- Test None handling in transform chain

### Test Strategy

**Unit Testing:**
- Each validator method tested in isolation
- Each transform configuration tested in isolation
- Edge cases: empty strings, None values, boundary conditions

**Integration Testing:**
- Create real Pydantic models using the validators/types
- Test model instantiation with valid data
- Test model instantiation with invalid data (expect ValidationError)
- Test model serialization/deserialization (model_dump, model_validate)
- Test chaining transforms from multiple utility classes

**Error Testing:**
- Verify appropriate ValidationError messages
- Test validator behavior with wrong types
- Test edge cases that should fail
- Test behavior when transform function raises exception

## Risks & Rollback

### Risks

1. **Pydantic API Changes**: Pydantic 2 is stable, but future versions might change validation approach
   - *Mitigation*: Pin to `pydantic>=2.0.0,<3.0.0` and test thoroughly with current version

2. **Naming Conflicts**: Class names Validator and Types are generic, could conflict
   - *Mitigation*: Export with "Pydantic" prefix (PydanticValidator, PydanticTypes) from main utils package to distinguish from standalone Validator class

3. **Type Hint Complexity**: Annotated types can be complex for users unfamiliar with Pydantic 2
   - *Mitigation*: Provide clear examples and documentation showing typical usage patterns

4. **Transform Function Compatibility**: Not all functions are suitable as transforms
   - *Mitigation*: Document requirements for transform functions (must accept value as first param, return transformed value)

5. **Error Messages**: When transform fails, error message might not be clear
   - *Mitigation*: Wrap transforms in try/except and provide informative error messages

6. **Performance**: Chaining many transforms might slow down model instantiation
   - *Mitigation*: Keep transform chains reasonable, benchmark if needed, leverage Pydantic's optimization

7. **Compatibility**: JsonDB already uses Pydantic BaseModel, need to ensure no breaking changes
   - *Mitigation*: Test JsonDB thoroughly after adding new utilities, ensure backward compatibility

### Rollback Strategy

**If issues found after merge:**
1. Remove imports from `utils/__init__.py`
2. Remove package from exports (`__all__`)
3. Delete `utils/pydantic/` directory
4. Delete test files
5. Revert documentation changes
6. No impact on existing utils since this is purely additive

**Low Risk**: This feature is completely additive with no changes to existing utility classes. Users who don't import PydanticValidator or PydanticTypes won't be affected. JsonDB continues to work unchanged.

## Evidence

Discovery findings from codebase search:

1. **utils/__init__.py:1-54** — Shows export pattern with __all__ list, imports from subpackages
2. **utils/validator.py:1-100** — Existing Validator class with static methods for email, url, phone validation
3. **utils/string.py:1-80** — String class with slug, strip, case conversion methods (perfect for transforms)
4. **utils/integer.py** — Integer class with clamp, abs, and other methods (can be used as transforms)
5. **utils/db/json/json_db.py:1-100** — JsonDB uses Pydantic BaseModel, Field, already integrates Pydantic
6. **pyproject.toml:10-12** — Pydantic 2 is already a core dependency (pydantic>=2.0.0)
7. **CLAUDE.md:1-150** — Documents static utility pattern, keyword-only args, module organization
8. **tests/test_validation.py** — Existing validation tests follow pattern for new Pydantic validator tests
9. **tests/test_string.py** — Existing string tests show utility methods that can be used as transforms
10. **utils/db/json/__init__.py** — Shows package structure for multi-file utility modules
11. **README.md** — Documents all utility classes with usage examples and feature list

## Assumptions

1. Pydantic 2.x is the target version (already in dependencies)
2. Users are familiar with basic Pydantic model definition
3. Static utility pattern is preferred over class-based validators
4. Keyword-only arguments convention will be maintained
5. Integration with existing utils (String, Validator, Integer) is desirable
6. Test coverage should match existing utilities (comprehensive)
7. JsonDB compatibility must be maintained
8. No breaking changes to existing code are acceptable
9. Exporting with "Pydantic" prefix is acceptable to avoid naming conflicts with standalone Validator class
10. Transform functions follow convention: accept value as first param, return transformed value
11. Users understand that transforms must be unary functions (or use lambda/partial for multi-param functions)

## Open Questions

1. **Validator Return Types**: Should validators return specific error messages or use Pydantic defaults?
   - Suggestion: Allow customizable error messages via keyword args

2. **Transform Error Handling**: How should we handle when a transform function raises an exception?
   - Suggestion: Catch and re-raise as ValidationError with descriptive message

3. **Transform Function Signature**: Should we validate that transform functions have correct signature?
   - Suggestion: Trust users, provide clear documentation and examples

4. **Partial Functions**: Should we provide helper for creating partials of multi-param functions?
   - Suggestion: Document using functools.partial, don't create custom wrapper

5. **Composition Helpers**: Should we provide utilities for combining multiple validators?
   - Suggestion: Defer to Pydantic's built-in composition, document patterns

6. **Async Support**: Should validators or transforms support async?
   - Suggestion: Start with sync only, add async in future if needed

## Tasks

1. Create the package structure by adding utils/pydantic directory with init file
2. Implement Validator class in validator.py with factory methods for common validators
3. Implement Types class in types.py with transform factory method that accepts single or multiple transform functions
4. Create test file test_pydantic_validator.py with comprehensive validator tests
5. Create test file test_pydantic_types.py with comprehensive transform tests using existing utils
6. Update utils init file to import with aliases and export as PydanticValidator and PydanticTypes classes
7. Add Pydantic utilities section to README.md with usage examples showing transform composition
8. Update CLAUDE.md to document the new Pydantic utility classes in available utilities list
9. Run full test suite to ensure no regressions and all new tests pass
10. Run linting and type checking to ensure code quality standards are met
11. Verify JsonDB still works correctly with the new Pydantic utilities available
12. Update feature count and test count in README.md features section
