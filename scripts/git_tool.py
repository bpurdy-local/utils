#!/usr/bin/env python3
"""Git shortcuts - branch cleanup, log formatting, stats."""

import argparse
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path as PathLib

# Add parent directory to path to import utils
sys.path.insert(0, str(PathLib(__file__).parent.parent))

from utils import Terminal


def run_git(args: list[str], capture: bool = True) -> tuple[int, str, str]:
    """Run git command and return (returncode, stdout, stderr)."""
    result = subprocess.run(
        ["git"] + args,
        capture_output=capture,
        text=True,
    )
    return result.returncode, result.stdout.strip(), result.stderr.strip()


def cmd_branches(args: argparse.Namespace) -> int:
    """List branches with extra info."""
    code, output, _ = run_git([
        "for-each-ref",
        "--sort=-committerdate",
        "--format=%(refname:short)|%(committerdate:relative)|%(authorname)|%(subject)",
        "refs/heads/",
    ])

    if code != 0:
        return code

    # Get current branch
    _, current, _ = run_git(["branch", "--show-current"])

    print(f"\n{Terminal.colorize('Branches', color='cyan', bold=True)}")
    Terminal.print_line("─", width=80)

    for line in output.splitlines()[:args.limit]:
        parts = line.split("|")
        if len(parts) >= 4:
            branch, date, author, subject = parts[0], parts[1], parts[2], parts[3]

            if branch == current:
                branch = Terminal.colorize(f"* {branch}", color="green", bold=True)
            else:
                branch = f"  {branch}"

            print(f"{branch:<40} {date:<20} {author}")
            if args.verbose:
                print(f"    {Terminal.colorize(subject[:60], color='yellow')}")

    return 0


def cmd_cleanup(args: argparse.Namespace) -> int:
    """Clean up merged branches."""
    # Get merged branches
    code, output, _ = run_git(["branch", "--merged"])
    if code != 0:
        return code

    # Get current branch
    _, current, _ = run_git(["branch", "--show-current"])

    branches = []
    protected = {"main", "master", "develop", "dev", current}

    for line in output.splitlines():
        branch = line.strip().lstrip("* ")
        if branch and branch not in protected:
            branches.append(branch)

    if not branches:
        print(Terminal.colorize("No branches to clean up", color="green"))
        return 0

    print(f"\n{Terminal.colorize('Merged branches to delete:', color='cyan', bold=True)}")
    for branch in branches:
        print(f"  - {branch}")

    if args.dry_run:
        print(Terminal.colorize("\nDry run - no branches deleted", color="yellow"))
        return 0

    if not args.force:
        confirm = input("\nDelete these branches? [y/N]: ")
        if confirm.lower() != "y":
            print("Cancelled")
            return 0

    for branch in branches:
        code, _, err = run_git(["branch", "-d", branch])
        if code == 0:
            print(Terminal.colorize(f"Deleted: {branch}", color="green"))
        else:
            print(Terminal.colorize(f"Failed: {branch} - {err}", color="red"))

    return 0


def cmd_log(args: argparse.Namespace) -> int:
    """Pretty git log."""
    format_str = args.format

    formats = {
        "oneline": "%C(yellow)%h%C(reset) %s %C(dim)(%cr)%C(reset)",
        "short": "%C(yellow)%h%C(reset) %s%n  %C(dim)%an, %cr%C(reset)",
        "medium": "%C(yellow)%h%C(reset) %C(green)%ad%C(reset) %s%n  %C(cyan)%an%C(reset)",
        "full": "%C(yellow)commit %H%C(reset)%nAuthor: %an <%ae>%nDate:   %ad%n%n    %s%n",
        "graph": "--graph --oneline --decorate",
    }

    if format_str in formats:
        if format_str == "graph":
            git_args = ["log"] + formats[format_str].split() + [f"-{args.n}"]
        else:
            git_args = ["log", f"--format={formats[format_str]}", f"-{args.n}"]
    else:
        git_args = ["log", f"--format={format_str}", f"-{args.n}"]

    if args.author:
        git_args.append(f"--author={args.author}")
    if args.since:
        git_args.append(f"--since={args.since}")
    if args.until:
        git_args.append(f"--until={args.until}")
    if args.path:
        git_args.append("--")
        git_args.append(args.path)

    result = subprocess.run(["git"] + git_args)
    return result.returncode


def cmd_stats(args: argparse.Namespace) -> int:
    """Show repository statistics."""
    print(f"\n{Terminal.colorize('Repository Statistics', color='cyan', bold=True)}")
    Terminal.print_line("─", width=50)

    # Total commits
    _, total_commits, _ = run_git(["rev-list", "--count", "HEAD"])
    print(f"Total commits: {total_commits}")

    # Contributors
    _, contributors, _ = run_git(["shortlog", "-sn", "HEAD"])
    num_contributors = len(contributors.splitlines())
    print(f"Contributors: {num_contributors}")

    # First and last commit dates
    _, first_commit, _ = run_git(["log", "--reverse", "--format=%ad", "--date=short", "-1"])
    _, last_commit, _ = run_git(["log", "--format=%ad", "--date=short", "-1"])
    print(f"First commit: {first_commit}")
    print(f"Last commit: {last_commit}")

    # Files and lines
    _, files_count, _ = run_git(["ls-files"])
    print(f"Tracked files: {len(files_count.splitlines())}")

    # Branches
    _, branches, _ = run_git(["branch", "-a"])
    local = len([b for b in branches.splitlines() if not b.strip().startswith("remotes/")])
    remote = len([b for b in branches.splitlines() if b.strip().startswith("remotes/")])
    print(f"Branches: {local} local, {remote} remote")

    # Tags
    _, tags, _ = run_git(["tag"])
    print(f"Tags: {len(tags.splitlines()) if tags else 0}")

    if args.verbose:
        print(f"\n{Terminal.colorize('Top Contributors:', color='cyan')}")
        for line in contributors.splitlines()[:10]:
            parts = line.strip().split("\t")
            if len(parts) == 2:
                count, name = parts
                print(f"  {count.strip():>6}  {name}")

    return 0


def cmd_recent(args: argparse.Namespace) -> int:
    """Show recently modified files."""
    code, output, _ = run_git([
        "log",
        "--name-only",
        "--pretty=format:",
        f"-{args.commits}",
    ])

    if code != 0:
        return code

    files = {}
    for line in output.splitlines():
        line = line.strip()
        if line:
            files[line] = files.get(line, 0) + 1

    print(f"\n{Terminal.colorize('Recently Modified Files', color='cyan', bold=True)}")
    Terminal.print_line("─", width=60)

    sorted_files = sorted(files.items(), key=lambda x: x[1], reverse=True)
    for file, count in sorted_files[:args.limit]:
        print(f"  {count:>3}x  {file}")

    return 0


def cmd_undo(args: argparse.Namespace) -> int:
    """Undo last commit (keep changes)."""
    if args.hard:
        print(Terminal.colorize("WARNING: This will discard changes!", color="red", bold=True))
        confirm = input("Are you sure? [y/N]: ")
        if confirm.lower() != "y":
            print("Cancelled")
            return 0
        code, _, err = run_git(["reset", "--hard", "HEAD~1"])
    else:
        code, _, err = run_git(["reset", "--soft", "HEAD~1"])

    if code == 0:
        print(Terminal.colorize("Last commit undone", color="green"))
    else:
        print(Terminal.colorize(f"Error: {err}", color="red"))

    return code


def cmd_stash_list(args: argparse.Namespace) -> int:
    """List stashes with details."""
    code, output, _ = run_git(["stash", "list", "--format=%gd|%gs|%cr"])

    if code != 0:
        return code

    if not output:
        print(Terminal.colorize("No stashes", color="yellow"))
        return 0

    print(f"\n{Terminal.colorize('Stashes', color='cyan', bold=True)}")
    Terminal.print_line("─", width=60)

    for line in output.splitlines():
        parts = line.split("|")
        if len(parts) >= 3:
            ref, msg, date = parts[0], parts[1], parts[2]
            print(f"  {Terminal.colorize(ref, color='yellow')}  {date}")
            print(f"    {msg}")
            print()

    return 0


def cmd_alias(args: argparse.Namespace) -> int:
    """List or set git aliases."""
    if args.name and args.command:
        # Set alias
        code, _, err = run_git(["config", "--global", f"alias.{args.name}", args.command])
        if code == 0:
            print(Terminal.colorize(f"Alias set: {args.name} = {args.command}", color="green"))
        else:
            print(Terminal.colorize(f"Error: {err}", color="red"))
        return code
    else:
        # List aliases
        code, output, _ = run_git(["config", "--get-regexp", "^alias\\."])
        if code != 0 or not output:
            print(Terminal.colorize("No aliases configured", color="yellow"))
            return 0

        print(f"\n{Terminal.colorize('Git Aliases', color='cyan', bold=True)}")
        Terminal.print_line("─", width=60)

        for line in sorted(output.splitlines()):
            parts = line.split(" ", 1)
            if len(parts) == 2:
                name = parts[0].replace("alias.", "")
                cmd = parts[1]
                print(f"  {Terminal.colorize(name, color='yellow'):20} {cmd}")

        return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Git shortcuts - branch management, logs, stats, cleanup.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # List branches with last commit info
  python git_tool.py branches
  # Output: * main           2 hours ago   John Doe
  #           feature-x      3 days ago    Jane Smith

  # Show commit messages too
  python git_tool.py branches -v

  # Clean up merged branches
  python git_tool.py cleanup
  # Shows merged branches and asks for confirmation

  # Dry run (just show what would be deleted)
  python git_tool.py cleanup -n

  # Delete without confirmation
  python git_tool.py cleanup -f

  # Pretty git log
  python git_tool.py log
  python git_tool.py log -n 50                    # last 50 commits
  python git_tool.py log -f graph                 # graph view
  python git_tool.py log -a "John"                # filter by author
  python git_tool.py log --since "1 week ago"     # recent commits
  python git_tool.py log src/main.py              # commits for file

  # Repository statistics
  python git_tool.py stats
  # Output: Total commits: 1234
  #         Contributors: 15
  #         First commit: 2022-01-01
  #         Tracked files: 150

  # Show top contributors
  python git_tool.py stats -v

  # Recently modified files
  python git_tool.py recent
  # Output: 12x  src/main.py
  #          8x  tests/test_main.py

  # Undo last commit (keep changes staged)
  python git_tool.py undo

  # Undo and discard changes (dangerous!)
  python git_tool.py undo --hard

  # List stashes with details
  python git_tool.py stashes

  # Manage git aliases
  python git_tool.py alias                    # list all aliases
  python git_tool.py alias st "status -sb"   # create alias
""",
    )
    subparsers = parser.add_subparsers(dest="command", help="Command")

    # Branches
    p = subparsers.add_parser("branches", aliases=["br"], help="List branches with info")
    p.add_argument("-n", "--limit", type=int, default=20, help="Max branches to show")
    p.add_argument("-v", "--verbose", action="store_true", help="Show commit messages")
    p.set_defaults(func=cmd_branches)

    # Cleanup
    p = subparsers.add_parser("cleanup", help="Delete merged branches")
    p.add_argument("-n", "--dry-run", action="store_true", help="Show what would be deleted")
    p.add_argument("-f", "--force", action="store_true", help="Don't ask for confirmation")
    p.set_defaults(func=cmd_cleanup)

    # Log
    p = subparsers.add_parser("log", aliases=["l"], help="Pretty git log")
    p.add_argument("-n", type=int, default=20, help="Number of commits")
    p.add_argument("-f", "--format", default="oneline",
                   help="Format: oneline, short, medium, full, graph, or custom")
    p.add_argument("-a", "--author", help="Filter by author")
    p.add_argument("--since", help="Commits since date")
    p.add_argument("--until", help="Commits until date")
    p.add_argument("path", nargs="?", help="File path to filter")
    p.set_defaults(func=cmd_log)

    # Stats
    p = subparsers.add_parser("stats", help="Repository statistics")
    p.add_argument("-v", "--verbose", action="store_true", help="Show more details")
    p.set_defaults(func=cmd_stats)

    # Recent
    p = subparsers.add_parser("recent", help="Recently modified files")
    p.add_argument("-n", "--commits", type=int, default=50, help="Commits to scan")
    p.add_argument("-l", "--limit", type=int, default=20, help="Files to show")
    p.set_defaults(func=cmd_recent)

    # Undo
    p = subparsers.add_parser("undo", help="Undo last commit")
    p.add_argument("--hard", action="store_true", help="Discard changes")
    p.set_defaults(func=cmd_undo)

    # Stash list
    p = subparsers.add_parser("stashes", help="List stashes")
    p.set_defaults(func=cmd_stash_list)

    # Alias
    p = subparsers.add_parser("alias", help="Manage aliases")
    p.add_argument("name", nargs="?", help="Alias name")
    p.add_argument("command", nargs="?", help="Git command")
    p.set_defaults(func=cmd_alias)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 0

    try:
        return args.func(args)
    except Exception as e:
        print(Terminal.colorize(f"Error: {e}", color="red"), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
