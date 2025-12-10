# Production Readiness Check

Perform a comprehensive scan to determine if the project is production-ready.

## How This Check Works

This command performs a deep analysis across 10 categories, generating a detailed report with findings and recommendations.

---

## Check Categories

### 1. Code Quality (Automated)
**What we check:**
- Run linter (`ruff check .`) - any errors?
- Run formatter check (`ruff format --check .`) - any unformatted code?
- Run type checker (`pyright`) - any type errors?
- Check for `# TODO`, `# FIXME`, `# HACK` comments
- Check for `print()` statements (should use logging)
- Check for `breakpoint()` or `pdb` left in code

**Commands:**
```bash
.venv/bin/ruff check .
.venv/bin/ruff format --check .
.venv/bin/pyright
grep -rn "# TODO\|# FIXME\|# HACK" --include="*.py" .
grep -rn "print(" --include="*.py" . | grep -v "test_\|__pycache__"
grep -rn "breakpoint()\|import pdb\|pdb.set_trace" --include="*.py" .
```

### 2. Test Coverage
**What we check:**
- Do tests exist for all modules?
- What's the coverage percentage?
- Are edge cases tested?
- Are error conditions tested?

**Commands:**
```bash
.venv/bin/pytest --cov=utils --cov-report=term-missing
# Look for files with < 80% coverage
```

**Criteria:**
- [ ] Coverage > 80% overall
- [ ] All public methods have tests
- [ ] Edge cases covered (empty inputs, None, boundaries)
- [ ] Error paths tested

### 3. Security
**What we check:**
- Hardcoded secrets (API keys, passwords, tokens)
- SQL injection vulnerabilities (if applicable)
- Command injection (subprocess with shell=True)
- Unsafe deserialization (pickle, yaml.load without Loader)
- Sensitive data in logs

**Commands:**
```bash
# Check for hardcoded secrets patterns
grep -rn "api_key\|password\|secret\|token" --include="*.py" . | grep -v "test_\|\.pyc"
grep -rn "BEGIN RSA\|BEGIN PRIVATE" --include="*.py" .

# Check for dangerous patterns
grep -rn "shell=True" --include="*.py" .
grep -rn "pickle.load\|yaml.load" --include="*.py" .
grep -rn "eval(\|exec(" --include="*.py" .
```

### 4. Error Handling
**What we check:**
- Are exceptions caught appropriately?
- Are error messages clear and actionable?
- Is there bare `except:` (catches everything including KeyboardInterrupt)?
- Are errors logged?

**Commands:**
```bash
# Find bare except clauses
grep -rn "except:" --include="*.py" . | grep -v "except:$"

# Find broad exception catching
grep -rn "except Exception" --include="*.py" .
```

**Review:**
- Read through exception handling in key modules
- Check that errors have context (what failed, what input caused it)
- Verify no sensitive data in error messages

### 5. Documentation
**What we check:**
- Do all public classes/functions have docstrings?
- Is there a README with setup instructions?
- Are complex algorithms explained?
- Is the API documented?

**Commands:**
```bash
# Find functions/methods without docstrings
# (Manual review needed - check key modules)

# Check README exists and has content
wc -l README.md
```

**Criteria:**
- [ ] README with installation, usage, examples
- [ ] All public methods have docstrings
- [ ] Complex logic has inline comments
- [ ] API reference available (if applicable)

### 6. Dependencies
**What we check:**
- Are versions pinned appropriately?
- Are there known vulnerabilities?
- Are dependencies up to date?
- Are there unused dependencies?

**Commands:**
```bash
# Check for unpinned dependencies
cat pyproject.toml | grep -A 50 "dependencies"

# Check for vulnerabilities (if pip-audit installed)
pip-audit

# List outdated packages
pip list --outdated
```

### 7. Configuration
**What we check:**
- Are secrets in environment variables (not hardcoded)?
- Is there a `.env.example` for required env vars?
- Are defaults sensible for production?
- Is configuration validated?

**Files to check:**
- `.env.example` or similar
- Config loading code
- Default values in code

### 8. Logging
**What we check:**
- Is logging configured (not just print statements)?
- Are log levels appropriate?
- Is sensitive data excluded from logs?
- Are errors logged with context?

**Commands:**
```bash
# Check for logging setup
grep -rn "import logging\|from.*logging" --include="*.py" .
grep -rn "logger\.\|logging\." --include="*.py" .
```

### 9. Performance
**What we check:**
- Any obvious O(n²) or worse algorithms on large data?
- Are there memory leaks (growing caches, unclosed resources)?
- Are database queries optimized (if applicable)?
- Are expensive operations cached where appropriate?

**Review:**
- Look for nested loops on collections
- Check for resource cleanup (files, connections)
- Review any caching logic

### 10. Operational Readiness
**What we check:**
- Is there CI/CD configuration?
- Are there health checks (if it's a service)?
- Is there monitoring/alerting setup?
- Is there a deployment process documented?

**Files to check:**
- `.github/workflows/` or similar CI config
- `Dockerfile` if containerized
- Deployment documentation

---

## Output Format

Generate a report in `claude/references/prod-readiness-report.md`:

```markdown
# Production Readiness Report
Generated: YYYY-MM-DD

## Summary
| Category | Status | Issues |
|----------|--------|--------|
| Code Quality | ✅ Pass / ⚠️ Warning / ❌ Fail | Count |
| Test Coverage | ... | ... |
| Security | ... | ... |
| Error Handling | ... | ... |
| Documentation | ... | ... |
| Dependencies | ... | ... |
| Configuration | ... | ... |
| Logging | ... | ... |
| Performance | ... | ... |
| Operational | ... | ... |

**Overall: READY / NOT READY / NEEDS REVIEW**

## Detailed Findings

### Category Name
**Status:** ✅ Pass / ⚠️ Warning / ❌ Fail

**Findings:**
- Finding 1
- Finding 2

**Recommendations:**
- [ ] Action item 1
- [ ] Action item 2

---
(Repeat for each category)
```

## Severity Levels

- **❌ Blocker**: Must fix before production (security issues, crashes, data loss)
- **⚠️ Warning**: Should fix, but not blocking (missing tests, TODOs, minor issues)
- **ℹ️ Info**: Nice to have, low priority (style, minor improvements)
