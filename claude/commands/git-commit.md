# Git Commit

Create a clean, well-formatted git commit.

## Arguments
- `$MESSAGE`: Optional commit message (will be generated if not provided)

## Instructions

### 1. Review Changes
```bash
# See what files changed
git status

# See the actual changes
git diff

# See staged changes
git diff --cached
```

### 2. Stage Changes
```bash
# Stage specific files
git add path/to/file.py

# Stage all changes in a directory
git add utils/

# Interactive staging (select hunks)
git add -p
```

### 3. Commit Message Format
```
<type>: <short summary>

<optional body with more details>

<optional footer with ticket reference>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `refactor`: Code change that neither fixes a bug nor adds a feature
- `test`: Adding or updating tests
- `docs`: Documentation changes
- `chore`: Maintenance tasks

**Examples:**
```bash
git commit -m "feat: Add String.slugify method for URL-safe strings"

git commit -m "fix: Handle empty list in Iterable.chunk

Previously raised IndexError on empty input.
Now returns empty list as expected.

Fixes UTIL-456"

git commit -m "refactor: Simplify Datetime.parse logic"
```

### 4. Best Practices
- Keep commits atomic (one logical change per commit)
- Write clear, descriptive messages
- Use present tense ("Add feature" not "Added feature")
- Reference ticket numbers when applicable
- Don't commit debug code or print statements
- Don't commit commented-out code

### 5. Before Committing
- [ ] Run tests: `pytest`
- [ ] Run linter: `ruff check .`
- [ ] Review diff one more time
- [ ] Ensure no sensitive data (secrets, credentials) is included
