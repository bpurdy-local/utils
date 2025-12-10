# Execute Plan

Execute a previously created and approved implementation plan.

## Arguments
- `$NAME`: Name of the plan file (without .md), e.g., "auth-refactor"

## Prerequisites
- Plan must exist at `claude/plans/$NAME.md`
- Plan must be reviewed and approved by the user

## Instructions

### 1. Load the Plan

Read the plan from `claude/plans/$NAME.md` and confirm:
- The plan exists
- Status shows "Approved" (update it if user just approved)
- All steps are clear

### 2. Update Plan Status

Change the status in the plan file:
```markdown
**Status:** In Progress
```

### 3. Execute Steps

For each implementation step in the plan:

1. Mark step as in-progress in the plan file
2. Implement the change
3. Run relevant tests
4. Mark step as complete: `1. [x] Step description`
5. Move to next step

### 4. Quality Checks

After implementation, run quality checks (see `claude/TOOLS.md`):

```bash
# Typical checks
ruff check --fix .
ruff format .
pyright  # or mypy
pytest
```

### 5. Update Plan Status

When complete, update the plan file:
```markdown
**Status:** Complete
**Completed:** YYYY-MM-DD
```

### 6. Completion Report

Provide a summary:

```markdown
## Execution Complete: $NAME

### Completed Steps
- [x] Step 1
- [x] Step 2
- [x] Step 3

### Files Changed
- `path/to/file.py` - What was done
- `tests/test_file.py` - Tests added

### Test Results
- X tests added
- All tests passing

### Notes
Any observations, follow-ups, or issues encountered.
```

## Handling Deviations

If you need to deviate from the plan:
1. Stop and explain why
2. Get approval for the change
3. Update the plan file with the deviation
4. Continue execution

## Rollback

If execution fails critically:
```bash
# Discard all changes
git checkout -- .

# Or stash for later review
git stash save "failed: $NAME"
```

Update plan status to "Failed" with notes on what went wrong.
