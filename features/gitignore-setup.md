# Feature Plan: Setup .gitignore File

**Created**: 2025-11-15

## Summary

This is a new GitHub project (git repository just initialized) that currently lacks a .gitignore file. The project is a Python utility library with minimal JavaScript/TypeScript tooling. Currently, Python cache files, virtual environments, test artifacts, IDE directories, and other build artifacts are being tracked in the directory. A proper .gitignore file is needed to prevent these temporary and generated files from being committed to version control.

The project structure includes:
- Python package (`utils/`) with source code
- Test suite (`tests/`)
- Virtual environment (`.venv/`)
- Python cache directories (`__pycache__/`)
- Pytest cache (`.pytest_cache/`)
- Ruff cache (`.ruff_cache/`)
- VSCode settings (`.vscode/`)
- JavaScript/TypeScript configuration (minimal, for linting/formatting)
- UV lock file for Python dependencies

## Acceptance Criteria

- [ ] .gitignore file is created at repository root
- [ ] Python bytecode files (.pyc) are ignored
- [ ] Python cache directories (__pycache__/) are ignored
- [ ] Virtual environment directories (.venv/, venv/, env/) are ignored
- [ ] Test and coverage artifacts (.pytest_cache/, .coverage, htmlcov/) are ignored
- [ ] Linter/formatter caches (.ruff_cache/, .mypy_cache/) are ignored
- [ ] Python build artifacts (dist/, build/, *.egg-info/) are ignored
- [ ] IDE directories (.vscode/, .idea/) are ignored
- [ ] OS-specific files (.DS_Store, Thumbs.db) are ignored
- [ ] Node.js directories (node_modules/) are ignored
- [ ] JavaScript build artifacts are ignored
- [ ] Environment variable files (.env, .env.local) are ignored
- [ ] The .gitignore follows standard Python and JavaScript/TypeScript best practices

## Scope/Non-Goals

### In Scope
- Create comprehensive .gitignore file covering Python development
- Include JavaScript/TypeScript ignore patterns (minimal usage in this project)
- Include common IDE and OS-specific patterns
- Include test and coverage artifact patterns
- Include build and distribution artifact patterns
- Include environment and secret file patterns
- Organize .gitignore with clear sections and comments

### Non-Goals
- Removing already-committed files from git history (will require separate git commands if needed)
- Creating .gitignore templates for other languages not used in this project
- Setting up git hooks or pre-commit configurations (already exists)
- Configuring git attributes or other git configuration files

## Files to Modify

### Files to Create
- `.gitignore` - New file at repository root containing comprehensive ignore patterns for Python, JavaScript/TypeScript, IDEs, OS files, and build artifacts

### Files NOT to Modify
- No existing files need modification
- This is purely additive (creating a new file)

## Design/Approach

The .gitignore file will be organized into clear sections for maintainability:

1. **Python Section**
   - Bytecode files (*.pyc, *.pyo, *.pyd)
   - Cache directories (__pycache__/)
   - Virtual environments (.venv/, venv/, env/, ENV/)
   - Distribution and build directories (dist/, build/, *.egg-info/, *.egg/)
   - Testing artifacts (.pytest_cache/, .coverage, htmlcov/, .tox/)
   - Type checking and linting caches (.mypy_cache/, .ruff_cache/, .pytype/)
   - Jupyter notebook checkpoints (.ipynb_checkpoints/)

2. **JavaScript/TypeScript Section**
   - Node modules (node_modules/)
   - Build output (dist/, build/)
   - Dependency lock files that shouldn't be committed (package-lock.json - though npm is not used here)
   - Cache directories (.npm/, .yarn/)

3. **IDE and Editor Section**
   - VSCode (.vscode/ - though some teams commit settings, user preference)
   - PyCharm/IntelliJ (.idea/)
   - Vim swap files (*.swp, *.swo)
   - Emacs backups (*~, \#*\#)

4. **OS-Specific Section**
   - macOS (.DS_Store, ._*)
   - Windows (Thumbs.db, Desktop.ini)
   - Linux (*~)

5. **Environment and Secrets Section**
   - Environment files (.env, .env.local, .env.*.local)
   - Secret files (secrets.*, *.key, *.pem - unless specifically needed)

6. **Build and Coverage Section**
   - Coverage reports (coverage.xml, .coverage.*)
   - Documentation builds (docs/_build/)

### Design Decisions

**Include .vscode/ in .gitignore**: While some teams commit VSCode settings for consistency, it's generally better to keep IDE configurations personal. The project already has .editorconfig for cross-editor consistency.

**Include uv.lock**: DECISION NEEDED - uv.lock is similar to requirements.lock and should typically be committed for reproducible builds. Will NOT include in .gitignore.

**Granular Python patterns**: Use comprehensive Python patterns covering bytecode, caches, builds, and common tool artifacts to ensure clean repository.

**Comments in .gitignore**: Include section headers as comments for maintainability and clarity.

## Tests to Add/Update

### No Automated Tests Needed
This is a configuration file that doesn't require automated testing.

### Manual Testing Steps
1. Create the .gitignore file
2. Run `git status` to verify previously untracked artifacts are now ignored
3. Verify that __pycache__ directories are ignored
4. Verify that .pytest_cache is ignored
5. Verify that .ruff_cache is ignored
6. Verify that .venv is ignored
7. Create a test .pyc file and verify it's ignored
8. Verify that source code files (.py) are still tracked
9. Verify that configuration files (pyproject.toml, package.json) are still tracked

## Risks & Rollback

### Risks
1. **Over-ignoring**: Might accidentally ignore files that should be committed (e.g., important configuration files)
2. **Already-committed files**: Files already committed won't be removed by adding .gitignore (requires git rm --cached)
3. **Team workflow disruption**: If .vscode/ is ignored but team expects shared settings

### Mitigation Strategies
1. **Conservative patterns**: Use specific patterns rather than overly broad wildcards
2. **Review git status**: Check git status output after creating .gitignore to ensure source files are still tracked
3. **Documentation**: Add comments in .gitignore explaining each section
4. **Standard patterns**: Use well-established Python and JavaScript ignore patterns from community templates

### Rollback Plan
- If .gitignore causes issues, simply delete the file with `rm .gitignore`
- Use `git checkout .gitignore` to restore a previous version if needed
- No risk of data loss since .gitignore only affects git tracking, not file deletion

## Evidence

**Current directory state shows files that should be ignored:**
- `.pytest_cache/` - Pytest cache directory exists and should be ignored
- `.ruff_cache/` - Ruff linter cache directory exists and should be ignored
- `.venv/` - Virtual environment directory exists and should be ignored
- `utils/__pycache__/` - Python cache directories exist throughout codebase
- `tests/__pycache__/` - Python cache directories in test directory
- Multiple .pyc files in __pycache__ directories

**Project configuration files show language ecosystem:**
- `pyproject.toml:1` - Python project configuration using modern pyproject.toml
- `package.json:1` - Minimal JavaScript/TypeScript tooling for linting
- `tsconfig.json` - TypeScript configuration exists (from directory listing)
- `.pre-commit-config.yaml` - Pre-commit hooks configured

**Python version and tooling:**
- `pyproject.toml:5` - Requires Python 3.11+
- `pyproject.toml:17` - Uses Ruff for linting
- `pyproject.toml:29` - Uses Pyright for type checking
- `uv.lock` - Uses uv for dependency management

**IDE configuration:**
- `.vscode/` directory exists with settings and extensions
- `.editorconfig` exists for cross-editor consistency

**OS evidence:**
- Running on macOS (from ls output showing Darwin filesystem attributes)
- .DS_Store files likely to be generated

## Assumptions

1. The project uses git for version control (confirmed by .git/ directory)
2. Standard Python development practices apply (pytest, ruff, pyright)
3. Virtual environment should never be committed (.venv/)
4. Build artifacts should never be committed
5. IDE settings are personal preference and shouldn't be committed
6. The uv.lock file should be committed for reproducible builds (like requirements.lock)
7. No sensitive data is currently in the repository

## Open Questions

1. Should .vscode/ be committed for team consistency, or ignored for personal preference?
   - **Recommendation**: Ignore it, since .editorconfig provides cross-editor consistency
2. Should coverage reports (htmlcov/, .coverage) be ignored?
   - **Recommendation**: Yes, ignore them - coverage reports are generated artifacts
3. Are there any project-specific files or directories that should be ignored?
   - Will use standard patterns, user can customize later
4. Should the features/ directory be committed?
   - **Recommendation**: Yes, feature plans should be tracked in version control

## Tasks

1. Research standard Python gitignore patterns from GitHub's gitignore templates
2. Research standard Node.js/JavaScript gitignore patterns for minimal tooling
3. Identify all Python-specific patterns needed (bytecode, cache, venv, build, test artifacts)
4. Identify all IDE and editor patterns (VSCode, PyCharm, Vim, Emacs)
5. Identify all OS-specific patterns (macOS, Windows, Linux)
6. Identify environment and secrets patterns
7. Organize patterns into logical sections with comments
8. Create .gitignore file at repository root with all identified patterns
9. Run git status to verify cache directories and artifacts are now ignored
10. Verify source code files are still tracked
11. Verify configuration files are still tracked
12. Test with a sample .pyc file to ensure bytecode is ignored
13. Document the .gitignore structure in comments within the file
