# Global Registry Utility

## Summary

Create a global registry utility that allows developers to register key-value pairs in one location and retrieve them anywhere else in the codebase without passing parameters through multiple function calls. This solves the problem of "prop drilling" where the same configuration values, dependencies, or settings need to be passed through many layers of function calls. The registry acts as a centralized store for application-wide values that can be accessed statically from any module.

This is useful for storing things like:
- Application configuration that doesn't change at runtime
- Shared service instances or dependencies
- Feature flags or environment-specific settings
- Constants that need to be accessed across modules

The registry should follow the existing utils pattern with static methods and support both simple key-value storage and optional namespacing for better organization.

## Acceptance Criteria

- [ ] Registry class created with static methods following existing utils pattern
- [ ] Can register a key-value pair and retrieve it later
- [ ] Can check if a key exists before retrieving
- [ ] Can unregister keys
- [ ] Can clear all registered values
- [ ] Can list all registered keys
- [ ] Supports optional namespacing to organize related values
- [ ] Thread-safe for concurrent access
- [ ] Raises clear errors when accessing non-existent keys
- [ ] Comprehensive test coverage for all operations
- [ ] Exported from main utils init file
- [ ] Documentation added to CLAUDE.md

## Scope/Non-Goals

### In Scope
- Static utility class with register, get, has, unregister, clear, list methods
- Optional namespace support for organizing values
- Thread-safe implementation using threading.Lock
- Type hints for all parameters and return values
- Default value support when getting non-existent keys
- Ability to require keys (raise error if missing)
- Get all values in a namespace
- Comprehensive unit tests covering edge cases

### Non-Goals
- Persistence to disk (registry values are in-memory only)
- Automatic serialization/deserialization of complex objects
- Change notification or observer pattern when values update
- Time-to-live or expiration for registry values
- Hierarchical nested namespaces (only one level of namespacing)
- Type validation of registered values
- Integration with dependency injection frameworks
- Automatic environment variable loading (use Env utility for that)

## Files to Modify

- **utils/registry.py** (new file): Create Registry class with static methods for registering and retrieving values. Include namespace support and thread-safe implementation using threading.Lock. Methods include register, get, has, unregister, clear, list_keys, get_namespace, and clear_namespace.

- **utils/__init__.py**: Add import for Registry class and include it in the __all__ export list.

- **tests/test_registry.py** (new file): Create comprehensive test suite covering basic registration and retrieval, namespace operations, thread safety, error conditions, default values, clearing operations, and edge cases like empty strings and None values.

- **CLAUDE.md**: Add Registry to the utilities section in module organization. Document it has approximately 10 methods including register, get with defaults, has, unregister, clear, list operations, and namespace support. Update test count.

- **README.md**: Add usage example showing basic registration and retrieval, namespace usage, and practical use case.

## Design/Approach

The Registry will be implemented as a static utility class following the established pattern in the utils library. It will use a class-level dictionary to store values and a threading.Lock for thread-safe operations.

The core storage will be a single dictionary where keys can optionally include a namespace prefix. For example, a key "api_key" in namespace "aws" would be stored internally as "aws:api_key". This allows simple namespacing without complex nested data structures.

All mutating operations (register, unregister, clear) will be protected by a lock to ensure thread safety. Read operations (get, has) will also use the lock to prevent reading during writes.

The API will follow keyword-only argument patterns like other utils, where the value to operate on comes first, followed by keyword-only parameters after the asterisk separator.

### Key Design Decisions

- **Threading.Lock over threading.local**: Unlike Logger which needs per-thread isolation, Registry should be shared across threads. We use Lock to synchronize access rather than thread-local storage.

- **Flat namespace with prefix convention**: Instead of nested dictionaries, use "namespace:key" string format. This keeps implementation simple while providing organizational benefits.

- **Keyword-only arguments**: Follow existing utils pattern where parameters after the first are keyword-only using asterisk separator.

- **Static methods only**: No instance creation needed, all operations are class-level static methods.

- **Explicit over implicit**: Require namespace parameter to be explicitly passed rather than having a default namespace. This makes code clearer.

- **No type enforcement**: Store any Python object without validation. Users are responsible for knowing what types they stored.

### Architecture Impact

This adds a new foundational utility to the utils library. It has no dependencies on other utils (except potentially for tests). Other modules could use Registry to avoid parameter passing, but it should be used judiciously to avoid creating hidden dependencies.

The Registry pattern can reduce coupling in some cases but can also make code harder to understand if overused. Documentation should emphasize using it for truly global, application-wide values rather than as a replacement for proper parameter passing.

### Data Flow

1. Early in application startup, register configuration values or service instances
2. Throughout the application lifecycle, modules can retrieve these values without imports or parameter passing
3. Values remain in memory until explicitly unregistered or application terminates
4. Thread-safe access allows concurrent reads and writes without race conditions

## Tests to Add/Update

- **Unit Tests**:
  - Test basic register and get operations
  - Test register with namespace and retrieve with namespace
  - Test has method for existing and non-existent keys
  - Test unregister removes keys correctly
  - Test clear removes all keys
  - Test clear_namespace only removes keys in that namespace
  - Test list_keys returns all registered keys
  - Test list_keys with namespace filter
  - Test get_namespace returns all values in a namespace
  - Test get with default value when key doesn't exist
  - Test get with required=True raises error when key missing
  - Test overwriting existing key values
  - Test namespace isolation (keys in different namespaces don't conflict)
  - Test empty string as key and value
  - Test None as value
  - Test concurrent access from multiple threads (register and get simultaneously)
  - Test error messages are clear and helpful

- **Integration Tests**:
  - Not needed - this is a standalone utility

- **Manual Testing**:
  - Import Registry and verify it works in Python REPL
  - Register a value, import Registry in another module, verify retrieval works
  - Test that registered values persist across imports but not across process restarts

## Risks & Rollback

### Risks

- **Overuse leading to hidden dependencies**: Developers might use Registry instead of proper dependency injection, making code harder to test and understand. Mitigation: Clear documentation on when to use vs not use, emphasize it's for truly global values only.

- **Thread safety bugs**: If lock implementation is incorrect, could have race conditions. Mitigation: Comprehensive thread safety tests, use proven threading.Lock pattern.

- **Memory leaks**: Values registered early in application might never be cleared. Mitigation: Document that values live for application lifetime, provide clear method to unregister.

- **Name collisions**: Different parts of code might use same key name. Mitigation: Encourage use of namespaces, document naming conventions.

### Rollback Plan

- Remove Registry from utils/__init__.py exports
- Delete utils/registry.py file
- Delete tests/test_registry.py file
- Remove documentation from CLAUDE.md and README.md
- No database migrations or data loss concerns since values are in-memory only

## Evidence

Discovered files and context:

- utils/logger.py:17 — Uses threading.local() for thread-safe context storage, similar pattern for global state
- utils/env.py — Static utility class pattern for environment variables, similar get/set operations
- utils/dict.py — Static utility for dictionary operations, similar pattern to follow
- utils/__init__.py — Shows export pattern for new utilities
- CLAUDE.md:123-126 — Documents utilities section where Registry will be added
- tests/test_env.py — Example test structure with multiple test classes for different functionality
- .claude/coding_standards.md:11-23 — Confirms OOP preference with static methods
- utils/session/session.py — Example of stateful class (counter-example, Registry should be stateless)

## Assumptions

- Users understand the difference between Registry (global application state) and environment variables (external configuration)
- Thread safety is required because web applications commonly use threading
- Namespaces are single-level (no nested namespaces like "aws:s3:bucket")
- Registry values are set during application startup and rarely change afterward
- No need for change notifications or observers when values are updated
- Users are working in single-process applications or understand Registry state isn't shared across processes
- Registered values can be any Python object (strings, ints, objects, functions, etc.)

## Open Questions

- [ ] Should we support dot notation for namespaces ("aws.s3.bucket") or stick with separator character?
- [ ] Should get method return a copy of mutable objects to prevent modification, or trust users?
- [ ] Do we need a register_many method for bulk registration, or is individual registration sufficient?
- [ ] Should we provide a context manager for temporary registrations?
- [ ] Should we log when values are overwritten, or is silent overwrite acceptable?

## Tasks

1. Create utils/registry.py file with Registry class definition
2. Implement internal storage dictionary and threading Lock as class variables
3. Implement register method that accepts key, value, and optional namespace parameter
4. Implement get method with support for default values and required flag
5. Implement has method to check key existence
6. Implement unregister method to remove keys
7. Implement clear method to remove all registered values
8. Implement list_keys method with optional namespace filter
9. Implement get_namespace method to retrieve all values in a namespace
10. Implement clear_namespace method to remove all keys in a namespace
11. Add Registry import to utils/__init__.py
12. Add Registry to __all__ list in utils/__init__.py
13. Create tests/test_registry.py with basic operation tests
14. Add namespace operation tests
15. Add thread safety tests with concurrent access
16. Add edge case tests (empty strings, None values, overwrites)
17. Add error condition tests (missing required keys, invalid operations)
18. Run full test suite to verify no regressions
19. Update CLAUDE.md with Registry documentation in utilities section
20. Update CLAUDE.md with new test count
21. Add usage examples to README.md showing practical use cases

---

**Notes**: This feature adds a global registry pattern to the utils library. It should be used sparingly for truly application-wide values. The implementation follows the established static utility class pattern and provides thread-safe access using threading.Lock similar to how Logger uses threading.local for thread-local context.
