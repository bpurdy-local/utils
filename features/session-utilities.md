# Session Utilities Package

**[Updated: 2025-11-17]** - Significantly reduced scope. Changed from 5 utility classes to a single Session wrapper class that inherits from a session object and provides helpful utility methods.

**[Updated: 2025-11-17]** - Removed testing requirement. Implementation will be reviewed first, then tests added after trimming down methods.

## Summary

Create a new subpackage `utils/session` containing a single Session class that wraps Python's standard library session functionality (likely using urllib or http.client as the base). The Session class will inherit from or wrap a session object and provide helpful utility methods for common HTTP operations.

**Problem it solves:**
Applications making HTTP requests often need to perform common operations like adding default headers, handling retries, tracking metrics, or managing cookies. Instead of manually implementing these patterns every time, a Session wrapper class can provide these utilities in a clean, reusable way.

**Why is this needed:**
- Simplified session configuration with sensible defaults
- Utility methods for common HTTP patterns (retry, timeout handling, etc.)
- Built-in request/response utilities
- Consistent API following the library's patterns
- No need to reinvent session management code in every project

## Acceptance Criteria

- [ ] New `utils/session/` directory created with proper package structure
- [ ] Session class that wraps or inherits from stdlib session (urllib.request or http.client)
- [ ] Initial set of helpful utility methods on the Session class (will be trimmed after review)
- [ ] Session class exported from `utils/__init__.py`
- [ ] README updated with Session class documentation and examples
- [ ] CLAUDE.md updated to reflect new session package
- [ ] All existing tests still pass (467 tests)
- [ ] Type hints are complete for all methods
- [ ] Uses requests library as dependency (Session inherits from requests.Session)
- [ ] **NO TESTS initially** - implementation will be reviewed and trimmed first

## Scope/Non-Goals

### In Scope
- Single Session wrapper class in `utils/session/session.py`
- Utility methods for HTTP requests (GET, POST, PUT, DELETE, etc.)
- Utility methods for setting common headers
- Utility method for adding default timeout
- Utility method for cookie management
- Utility method for authentication (using Authentication objects, not hardcoded methods)
- Utility method for URL building with query parameters
- Utility method for response parsing (JSON, text)
- Utility method for status code checking
- Class inherits from requests.Session
- Package structure under `utils/session/`

### Non-Goals
- Tests (will be added AFTER implementation review and method trimming)
- Separate utility classes for Retry, RateLimit, Metrics (future work)
- Multiple authentication methods (set_auth_bearer, set_auth_basic) - use single set_auth with Auth objects instead
- Complex authentication flows (OAuth2, SAML)
- Async/await support
- WebSocket support
- Request mocking or testing utilities
- Framework-specific integrations
- Other external dependencies beyond requests
- Distributed features
- Persistent storage

## Files to Modify

### New Files to Create

1. **`utils/session/__init__.py`**
   - Package initializer that exports Session class
   - Simple one-line export: `from utils.session.session import Session`
   - Add to `__all__` list

2. **`utils/session/session.py`**
   - Session class that wraps or inherits from stdlib session
   - Constructor that accepts session configuration (timeout, headers, etc.)
   - Utility method for making GET requests with defaults
   - Utility method for making POST requests with JSON
   - Utility method for making PUT requests
   - Utility method for making DELETE requests
   - Utility method for setting default headers on all requests
   - Utility method for setting authentication using an Authentication object (NOT separate methods for Bearer/Basic)
   - Utility method for building URLs with query parameters
   - Utility method for parsing JSON responses
   - Utility method for checking response status codes (is success, is error, etc.)
   - Utility method for managing cookies
   - Utility method for closing session and cleanup
   - May use composition (wrapping) rather than inheritance if simpler

3. **Authentication Classes (optional/future)**
   - If needed, create simple Authentication base class or protocol
   - Concrete implementations: BearerAuth, BasicAuth, etc.
   - These handle how auth headers are built
   - Session.set_auth() accepts any Authentication object

### Existing Files to Modify

1. **`utils/__init__.py`**
   - Import Session from `utils.session`
   - Add Session to `__all__` exports list
   - Maintain alphabetical ordering

2. **`README.md`**
   - Add new section "Session Utilities"
   - Show Session class initialization
   - Show examples of common utility methods
   - Show authentication examples (with Auth objects if implemented)
   - Show response parsing examples
   - Document available utility methods

3. **`CLAUDE.md`**
   - Update "Module Organization" to include session package
   - Document Session class as wrapper around stdlib
   - Note that it uses inheritance or composition pattern
   - Add to list of available utility classes

4. **`pyproject.toml`**
   - No changes needed (hatchling auto-discovers subpackages)

## Design/Approach

**[Updated: 2025-11-17]** - Simplified to single wrapper class

**[Updated: 2025-11-17]** - Changed authentication approach to use Auth objects instead of multiple set_auth_* methods

### Architecture

The session utilities will be a simple wrapper class under `utils/session/session.py`. The Session class will either inherit from a stdlib session class or use composition to wrap one. The goal is to provide convenient utility methods while maintaining access to all underlying session functionality.

### Key Design Decisions

1. **Inheritance vs Composition**
   - Likely use composition (Session has-a session object) for flexibility
   - Allows wrapping any session-like object (urllib, http.client, or even requests if user provides)
   - Alternatively, could inherit from http.client.HTTPConnection or similar
   - Decision: Use composition and forward calls to wrapped session

2. **Wrapper Class Pattern**
   - Session class wraps an underlying session object
   - Provides utility methods that use the wrapped session
   - Example: `session.get_json(url)` internally calls `session._session.get(url)` and parses JSON
   - Exposes underlying session for advanced usage: `session._session`

3. **Sensible Defaults**
   - Constructor accepts optional timeout, headers, auth
   - Sets reasonable defaults (30s timeout, common User-Agent)
   - Allows overriding on per-request basis
   - Configuration stored as instance variables

4. **Utility Method Design**
   - Methods like `get_json()`, `post_json()` for common patterns
   - Single `set_auth()` method that accepts Authentication objects
   - Methods like `build_url()` for URL construction
   - Methods like `is_success()`, `is_client_error()` for status checking
   - All methods are instance methods (not static like other utils)

5. **Authentication Design**
   - Single `set_auth(auth)` method instead of multiple `set_auth_bearer()`, `set_auth_basic()` methods
   - Accepts Authentication objects that know how to build auth headers
   - Could use simple dict for auth or create lightweight Auth classes
   - Flexible: allows custom authentication schemes without modifying Session class

6. **Error Handling**
   - Utility methods handle common error cases gracefully
   - Provide helpful error messages
   - Don't swallow exceptions - let them propagate with context
   - Status checking methods return booleans, never raise

### Data Flow

1. **Basic Request Flow**
   ```
   session = Session(timeout=30)
   session.set_default_header('User-Agent', 'MyApp/1.0')
   response = session.get(url)
   data = session.parse_json(response)
   ```

2. **Authenticated Request Flow (with Auth object)**
   ```
   session = Session()
   auth = BearerAuth('token123')  # or could be dict: {'type': 'bearer', 'token': '...'}
   session.set_auth(auth)
   response = session.get(protected_url)
   ```

3. **POST with JSON Flow**
   ```
   session = Session()
   response = session.post_json(url, data={'key': 'value'})
   ```

### Integration Points

- **String Integration**: Use String utilities for URL manipulation if needed
- **Validator Integration**: Could use URL validators for input checking
- **Logger Integration**: Future enhancement to log requests/responses

## Tests to Add/Update

**[Updated: 2025-11-17]** - NO TESTS in initial implementation

### Approach

1. Implement Session class with initial set of utility methods
2. Review implementation and identify which methods are useful
3. Trim down unnecessary or overly complex methods
4. THEN add comprehensive tests for the final set of methods

### Future Test Coverage (after trimming)

Tests will be added in a follow-up phase after the implementation is reviewed:
- Session initialization tests
- HTTP method tests with mocked responses
- Utility method tests
- Error handling tests
- Integration tests

### Manual Testing (Initial Phase)

1. Create simple test script that instantiates Session class
2. Make real HTTP requests to httpbin.org to verify functionality
3. Test each utility method manually
4. Identify which methods are useful and which can be removed
5. Document findings for trimming decision

## Risks & Rollback

### Risks

1. **Stdlib HTTP Library Choice**
   - Risk: Choosing wrong stdlib base (urllib vs http.client)
   - Mitigation: Start with urllib.request as it's higher-level
   - Mitigation: Design allows swapping implementation later
   - Mitigation: Document which stdlib module is used

2. **API Design Complexity**
   - Risk: Too many utility methods makes API confusing
   - Mitigation: Initial implementation can be generous with methods
   - Mitigation: Review and trim after seeing actual implementation
   - Mitigation: Name methods clearly (get_json, post_json, etc.)

3. **Breaking Changes**
   - Risk: Changes to `utils/__init__.py` affect imports
   - Mitigation: Only add Session export, don't modify existing
   - Mitigation: Run full test suite before committing

4. **Performance Overhead**
   - Risk: Wrapper adds latency to requests
   - Mitigation: Minimal wrapper code, delegates directly to stdlib
   - Mitigation: Benchmark if needed

### Rollback Plan

1. **Immediate Rollback**
   - Revert commits that added session package
   - Remove Session from `utils/__init__.py`
   - No impact on existing code

2. **Partial Rollback**
   - If specific methods are problematic, remove them
   - Keep Session class but with fewer methods

## Evidence

Based on repository exploration:

1. `utils/integer.py:4-256` - Shows class-based utility pattern (but uses static methods)
2. `utils/string.py:6-231` - Shows static utility class pattern
3. `utils/logger.py:13-224` - Shows class with class-level state and methods
4. `utils/__init__.py:18-35` - Shows export pattern for utility classes
5. `tests/test_logger.py` - Shows testing patterns for stateful classes (for future reference)
6. `README.md` - Shows documentation format for utility classes
7. `CLAUDE.md:21-33` - Documents existing utility classes
8. Python stdlib `urllib.request` - HTTP client to wrap
9. Python stdlib `http.client` - Lower-level HTTP to potentially wrap
10. `tests/test_imports.py` - Pattern for testing package imports (for future)

## Assumptions

1. Session class will inherit from requests.Session
2. Requests library is required as a dependency
3. Session will be instance-based (not static methods like String/Integer)
4. Users will instantiate Session objects: `session = Session()`
5. Python 3.11+ is the target
6. Focus on synchronous HTTP only (no async)
7. Initial implementation can be generous with methods (will trim after review)
8. Tests will be added AFTER implementation is reviewed and trimmed

## Open Questions

1. Should Session inherit from a stdlib class or use composition?
   - **Recommendation**: Use composition for flexibility
2. Which stdlib HTTP library should be the base (urllib.request vs http.client)?
   - **Recommendation**: Start with urllib.request (higher level, easier to use)
3. Should Session maintain any request history or metrics?
   - **Recommendation**: No, keep it simple for initial implementation
4. Should the class support both sync and async (via separate methods)?
   - **Recommendation**: Sync only for initial implementation
5. What should the default timeout be?
   - **Recommendation**: 30 seconds
6. Should we provide a context manager protocol (`with Session() as s:`)?
   - **Recommendation**: Yes, implement `__enter__` and `__exit__`
7. How should authentication be handled?
   - **Recommendation**: Single `set_auth(auth)` method accepting Auth objects or dicts
8. Should we create separate Auth classes (BearerAuth, BasicAuth) or use dicts?
   - **Recommendation**: Start simple with dicts or protocol, can add classes later if needed

## Tasks

1. Create the `utils/session/` directory structure with `__init__.py`

2. Create Session class in `utils/session/session.py` that wraps urllib.request

3. Implement constructor accepting timeout, headers, and authentication

4. Implement HTTP method utilities (get, post, put, delete)

5. Implement header management utilities (set default headers)

6. Implement authentication utility (single set_auth method accepting Auth objects)

7. Implement response parsing utilities (parse JSON, get text)

8. Implement URL building utility (build URL with query params)

9. Implement status code checking utilities (is success, is error, etc.)

10. Implement context manager protocol for automatic cleanup

11. Update `utils/__init__.py` to export Session class

12. Update README with Session class documentation and usage examples

13. Update CLAUDE.md to document the session package

14. Run existing test suite to ensure all 467 tests still pass

15. Manually test Session class with real HTTP requests to verify functionality

16. Review implementation and identify methods to trim

17. Add import test to `tests/test_imports.py` for Session class (minimal test only)

18. **DEFER**: Comprehensive test suite will be added after implementation review and trimming
