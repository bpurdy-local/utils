# Git Cleanup

Clean up git history, branches, and working directory.

## Arguments
- `$ACTION`: Type of cleanup (branches, stash, history, working-dir)

## Branch Cleanup

### Delete Merged Branches
```bash
# List merged branches (excluding main/master)
git branch --merged | grep -v "main\|master\|\*"

# Delete merged local branches
git branch --merged | grep -v "main\|master\|\*" | xargs -n 1 git branch -d

# Prune remote tracking branches
git fetch --prune

# Delete remote branches that no longer exist
git remote prune origin
```

### Delete Specific Branch
```bash
# Delete local branch
git branch -d branch-name

# Force delete unmerged branch
git branch -D branch-name

# Delete remote branch
git push origin --delete branch-name
```

## Stash Cleanup
```bash
# List stashes
git stash list

# Drop specific stash
git stash drop stash@{0}

# Clear all stashes
git stash clear
```

## Working Directory Cleanup
```bash
# Remove untracked files (dry run first)
git clean -n

# Remove untracked files
git clean -f

# Remove untracked files and directories
git clean -fd

# Remove ignored files too
git clean -fdx
```

## History Cleanup (Use with Caution)

### Amend Last Commit
```bash
# Change commit message
git commit --amend -m "New message"

# Add files to last commit
git add forgotten-file.py
git commit --amend --no-edit
```

### Interactive Rebase (local commits only)
```bash
# Rebase last N commits
git rebase -i HEAD~3

# Options in editor:
# pick - keep commit
# reword - change message
# squash - combine with previous
# drop - remove commit
```

## Safety Checks
- [ ] Don't rebase commits that have been pushed
- [ ] Don't force push to shared branches
- [ ] Create backup branch before risky operations: `git branch backup-branch`
- [ ] Use `--dry-run` or `-n` flags when available
