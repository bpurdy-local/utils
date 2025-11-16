# Analysis: String.snake_case vs Logger._normalize_key

## Summary

After reviewing both implementations, **I recommend keeping them separate** rather than consolidating. While they appear similar, they serve different purposes and have subtle behavioral differences.

## Implementation Comparison

### String.snake_case (utils/string.py:45-51)
```python
def snake_case(text: str) -> str:
    s = text.strip()
    s = re.sub(r"[^\w]+", "_", s)  # Replace non-word chars with underscores
    s = re.sub(r"(?<=[a-z0-9])([A-Z])", r"_\1", s)  # Insert underscore before capitals
    s = s.lower()
    s = re.sub(r"_+", "_", s).strip("_")  # Consolidate multiple underscores
    return s
```

### Logger._normalize_key (utils/logger.py:26-34)
```python
def _normalize_key(cls, key: str) -> str:
    # Convert keys to snake_case for consistent log field names
    # Handles: camelCase, PascalCase, kebab-case, spaces, consecutive caps
    key = re.sub(r'([a-z])([A-Z])', r'\1_\2', key)  # camelCase -> camel_Case
    key = re.sub(r'([A-Z]+)([A-Z][a-z])', r'\1_\2', key)  # HTTPServer -> HTTP_Server
    key = key.replace('-', '_').replace(' ', '_')  # kebab/spaces to underscores
    key = re.sub(r'_+', '_', key)  # Consolidate multiple underscores
    key = key.strip('_').lower()  # Trim and lowercase
    return key
```

## Key Differences

| Aspect | String.snake_case | Logger._normalize_key |
|--------|-------------------|------------------------|
| **Purpose** | General string transformation utility | Logging field name normalization |
| **Non-word chars** | Replaces ALL non-word chars with `_` | Only replaces `-` and ` ` with `_` |
| **Consecutive caps** | ✗ No special handling | ✓ Handles (e.g., "HTTPServer" → "http_server") |
| **Processing order** | Non-word → CamelCase → lowercase → consolidate | CamelCase → consecutive caps → replace → consolidate → lowercase |
| **Use case** | Converting arbitrary text to snake_case format | Normalizing log field keys (preserves more characters) |

## Behavioral Examples

### Test Case: "HTTP2Server-Name"

**String.snake_case:**
1. Strip: "HTTP2Server-Name"
2. Replace non-word: "HTTP2Server_Name"
3. Insert before caps: "HTTP2_Server__Name"
4. Lowercase: "http2_server__name"
5. Consolidate: "http2_server_name"
**Result:** `"http2_server_name"`

**Logger._normalize_key:**
1. camelCase pattern: "HTTP2Server-Name" (no match)
2. Consecutive caps: "HTTP2_Server-Name"
3. Replace -/space: "HTTP2_Server_Name"
4. Consolidate: "HTTP2_Server_Name"
5. Trim + lowercase: "http2_server_name"
**Result:** `"http2_server_name"`

### Test Case: "user@email.com"

**String.snake_case:**
1. Strip: "user@email.com"
2. Replace non-word: "user_email_com"
3. Insert before caps: "user_email_com"
4. Lowercase: "user_email_com"
5. Consolidate: "user_email_com"
**Result:** `"user_email_com"`

**Logger._normalize_key:**
1. camelCase pattern: "user@email.com" (no match)
2. Consecutive caps: "user@email.com" (no match)
3. Replace -/space: "user@email.com" (unchanged - @ is preserved)
4. Consolidate: "user@email.com"
5. Trim + lowercase: "user@email.com"
**Result:** `"user@email.com"` ← **Different!**

## Recommendation: Keep Separate

### Reasons:

1. **Different use cases**:
   - `String.snake_case`: General-purpose text transformation (sanitizes all special chars)
   - `Logger._normalize_key`: Log field normalization (preserves valid identifier chars like @, $, etc.)

2. **Performance consideration**:
   - Logger is in the hot path for every log call
   - Custom implementation is optimized for the specific logging use case
   - Adding a dependency on String class could introduce overhead

3. **Consecutive capitals handling**:
   - Logger has specialized logic for consecutive capitals (HTTPServer → http_server)
   - String.snake_case doesn't need this for general text transformation

4. **Character preservation**:
   - Logger preserves more characters (`@`, `.`, etc.) which may be intentional for field names
   - String.snake_case aggressively sanitizes to create clean identifiers

5. **Maintainability**:
   - Logger's implementation is self-contained and well-commented
   - No external dependencies keeps the logger module independent

### Conclusion:

**Decision: Keep both implementations separate.**

The methods serve different purposes:
- Use `String.snake_case()` for general text-to-identifier conversion
- Use `Logger._normalize_key()` for log field name normalization

If future requirements change and we need to consolidate, we could:
1. Add a `strict: bool` parameter to `String.snake_case()` to control character sanitization
2. Have `Logger._normalize_key()` delegate to `String.snake_case(text, strict=False)`
3. But for now, the separation is appropriate

## Implementation Notes

Both methods now have comprehensive inline comments explaining:
- What each regex pattern matches
- Why consecutive capitals get special handling (Logger only)
- The purpose of each transformation step
