# Plan Implementation

Create a detailed implementation plan for review before executing.

## Arguments
- `$TASK`: Description of the task or feature to plan
- `$NAME`: Short name for the plan file (e.g., "auth-refactor", "add-caching")

## Instructions

### 1. Understand the Requirements
- What is the desired outcome?
- What are the inputs and outputs?
- What are the constraints or limitations?
- Are there existing patterns to follow?

### 2. Research Phase
- Search the codebase for related functionality
- Identify files that will need changes
- Look for existing tests that show expected behavior
- Check for dependencies or side effects

### 3. Create the Plan File

Create the plan at `claude/plans/$NAME.md` (create the `plans/` directory if it doesn't exist):

```markdown
# Plan: $TASK

**Status:** Draft | Approved | In Progress | Complete
**Created:** YYYY-MM-DD

## Summary
Brief description of what will be implemented.

## Files to Modify
- `path/to/file1.py` - Description of changes
- `path/to/file2.py` - Description of changes

## Files to Create
- `path/to/new_file.py` - Purpose of new file

## Implementation Steps
1. [ ] First step with details
2. [ ] Second step with details
3. [ ] Third step with details

## Test Plan
- [ ] Test case 1: description
- [ ] Test case 2: description
- [ ] Edge case: description

## Considerations
- **Risk:** potential issue and mitigation
- **Alternative:** other approach considered and why not chosen
- **Dependency:** any external dependencies needed

## Scope
- [ ] Small (1-2 files, < 50 lines)
- [ ] Medium (3-5 files, 50-200 lines)
- [ ] Large (5+ files, 200+ lines)
```

### 4. Review Checklist
Before presenting the plan:
- [ ] All affected files identified
- [ ] No breaking changes to existing APIs (or migration noted)
- [ ] Test coverage plan included
- [ ] Edge cases considered
- [ ] Follows project patterns

### 5. Present for Approval

Tell the user:
- Plan saved to `claude/plans/$NAME.md`
- Summary of what will be done
- Ask for approval before executing

**DO NOT implement anything yet.** This command is for planning only.

Use `/execute $NAME` to execute an approved plan.
