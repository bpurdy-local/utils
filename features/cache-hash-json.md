# Cache, Hash, and JSON Utilities

## Summary

Add three new utilities to the utils library:
1. **Cache** - In-memory caching with TTL support and optional disk persistence
2. **Hash** - Hashing utilities for data integrity and security
3. **JSON** - Advanced JSON operations complementing existing Dict utility

These utilities fill common gaps without overlapping existing functionality. Cache provides memoization beyond the existing decorator, Hash handles data integrity and security hashing, and JSON provides advanced operations that complement Dict's transformation capabilities.

## Acceptance Criteria

**Cache Utility:**
- [ ] In-memory caching with TTL (time-to-live) support
- [ ] Optional disk-based persistent cache
- [ ] Cache invalidation (clear, clear_all, clear_expired)
- [ ] Cache statistics (hits, misses, size)
- [ ] Thread-safe implementation
- [ ] Namespace support for organizing cached values

**Hash Utility:**
- [ ] Support for common hash algorithms (MD5, SHA-1, SHA-256, SHA-512)
- [ ] Hash verification functionality
- [ ] File hashing capabilities
- [ ] String and bytes hashing
- [ ] Checksum generation for integrity checks
- [ ] HMAC support for secure hashing

**JSON Utility:**
- [ ] Pretty printing with customizable indentation
- [ ] JSON minification (remove whitespace)
- [ ] Flatten nested structures to dot notation
- [ ] Unflatten dot notation back to nested structure
- [ ] JSON schema validation (basic)
- [ ] Safe JSON parsing with error handling
- [ ] Does NOT duplicate Dict functionality (merge, deep operations, etc.)

**General:**
- [ ] All utilities follow static method pattern
- [ ] Comprehensive test coverage
- [ ] Thread-safe where applicable
- [ ] Type hints throughout
- [ ] Exported from main utils __init__
- [ ] Documentation in CLAUDE.md and README.md

## Scope/Non-Goals

### In Scope
- Cache: In-memory TTL cache, optional disk persistence, namespace support, statistics
- Hash: Common algorithms, file hashing, verification, HMAC
- JSON: Pretty/minify, flatten/unflatten, safe parsing, schema validation basics
- Thread safety for Cache (using threading.Lock)
- Static utility class pattern for all three
- Comprehensive unit tests

### Non-Goals
- Cache: Distributed caching, Redis/Memcached integration, LRU eviction policies beyond basic TTL
- Hash: Password hashing (use bcrypt/argon2 libraries), blockchain hashing
- JSON: Full JSON Schema validation (use jsonschema library), JSON Patch RFC implementation
- Overlap with existing Dict utility (merge, deep_get/set, transformations)
- Overlap with existing Encode/Decode (base64, URL encoding)
- Async versions (keep synchronous for consistency)

## Files to Modify

- **utils/cache.py** (new): Cache utility with in-memory and disk caching
- **utils/hash.py** (new): Hash utility for hashing and verification
- **utils/json_utils.py** (new): JSON utility for advanced JSON operations (named json_utils to avoid conflict with stdlib json)
- **utils/__init__.py**: Add imports and exports
- **tests/test_cache.py** (new): Comprehensive cache tests
- **tests/test_hash.py** (new): Comprehensive hash tests
- **tests/test_json_utils.py** (new): Comprehensive JSON tests
- **CLAUDE.md**: Document new utilities and update test count
- **README.md**: Add usage examples

## Design/Approach

### Cache Design
- Class-level storage dictionary with nested structure: `{namespace: {key: (value, expiry_time)}}`
- TTL stored as absolute timestamp (time.time() + ttl)
- Lazy expiration check on get (don't auto-clean, clean on access)
- Optional background cleanup thread for expired entries
- Disk cache uses pickle for serialization, stored in user-specified directory
- Statistics tracked: hits, misses, total requests, cache size

### Hash Design
- Thin wrapper around hashlib for common operations
- Support both string and bytes input
- File hashing reads in chunks to handle large files efficiently
- HMAC support for authenticated hashing
- Verification returns boolean (timing-safe comparison)

### JSON Design
- Flatten: `{"a": {"b": 1}}` → `{"a.b": 1}`
- Unflatten: reverse operation
- Pretty: wrapper around json.dumps with indent
- Minify: json.dumps with separators=(',', ':')
- Safe parse: try/except wrapper returning None or default on error
- Schema validation: basic type checking (not full JSON Schema spec)

### Key Design Decisions

1. **Cache TTL storage**: Store absolute expiry time rather than TTL duration for efficient expiration checking
2. **Lazy expiration**: Don't auto-clean expired entries, only remove on access to avoid background threads
3. **Hash algorithms**: Use hashlib for standard algorithms, no custom implementations
4. **JSON flatten separator**: Use dot notation (`.`) as default, customizable
5. **Avoid redundancy**: JSON utility does NOT duplicate Dict methods (merge, deep_get/set, transformations)
6. **Thread safety**: Cache needs Lock, Hash and JSON are stateless so thread-safe by design

## Tests to Add/Update

**Cache Tests (~30 tests):**
- Basic set/get with and without TTL
- Expiration behavior (expired entries return None)
- Namespace isolation
- Clear operations (single key, namespace, all, expired)
- Statistics tracking
- Thread safety with concurrent access
- Disk cache persistence and loading
- Edge cases (None values, zero TTL, negative TTL)

**Hash Tests (~25 tests):**
- Hash generation for all supported algorithms
- String vs bytes input
- File hashing (small and large files)
- Hash verification (matching and non-matching)
- HMAC generation and verification
- Checksum generation
- Edge cases (empty strings, empty files, None values)

**JSON Tests (~25 tests):**
- Pretty printing with different indents
- Minification
- Flatten/unflatten with various nesting levels
- Flatten with custom separators
- Safe parsing with valid and invalid JSON
- Schema validation (basic type checking)
- Edge cases (empty objects, arrays, None, special characters)
- Ensure no overlap with Dict functionality

## Risks & Rollback

### Risks
- **Cache memory usage**: In-memory cache could grow large. Mitigation: Provide clear() methods, document memory implications
- **Hash collision confusion**: Users might use MD5/SHA-1 for security. Mitigation: Document which algorithms are cryptographically secure
- **JSON flatten limitations**: Dot notation can conflict with actual dots in keys. Mitigation: Document limitation, provide custom separator

### Rollback Plan
- Remove new files: cache.py, hash.py, json_utils.py
- Remove test files
- Remove exports from __init__.py
- Revert CLAUDE.md and README.md changes

## Assumptions

- Users understand TTL is in seconds
- Disk cache directory is writable
- File hashing is for integrity checks, not real-time streaming
- JSON operations assume valid JSON structure (except safe_parse)
- Cache is single-process (not shared across processes)

## Open Questions

- [ ] Should Cache support LRU eviction in addition to TTL?
- [ ] Should Hash support password hashing (bcrypt wrapper)?
- [ ] Should JSON flatten handle array indices (e.g., `a.0.b`)?
- [ ] Should Cache have max size limit?

## Tasks

1. Create utils/cache.py with Cache class
2. Implement cache set/get with TTL support
3. Implement namespace support for cache
4. Implement cache statistics tracking
5. Implement cache clearing methods
6. Implement disk cache persistence (optional)
7. Add thread safety with Lock
8. Create utils/hash.py with Hash class
9. Implement hash methods (md5, sha1, sha256, sha512)
10. Implement file hashing
11. Implement hash verification
12. Implement HMAC support
13. Create utils/json_utils.py with JSON class
14. Implement pretty/minify methods
15. Implement flatten/unflatten
16. Implement safe parsing
17. Implement basic schema validation
18. Update utils/__init__.py with imports and exports
19. Create tests/test_cache.py with comprehensive tests
20. Create tests/test_hash.py with comprehensive tests
21. Create tests/test_json_utils.py with comprehensive tests
22. Run full test suite
23. Update CLAUDE.md documentation
24. Update README.md with examples

---

**Notes**: These three utilities fill clear gaps without overlapping existing functionality. Cache extends beyond the memoize decorator, Hash handles data integrity, and JSON provides advanced operations that complement (not duplicate) Dict's capabilities.
