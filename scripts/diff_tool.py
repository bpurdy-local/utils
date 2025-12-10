#!/usr/bin/env python3
"""File and directory diff with formatting options."""

import argparse
import difflib
import os
import sys
from pathlib import Path as PathLib

# Add parent directory to path to import utils
sys.path.insert(0, str(PathLib(__file__).parent.parent))

from utils import Path, Terminal


def read_lines(file_path: str) -> list[str]:
    """Read file lines."""
    return Path.read(file_path).splitlines(keepends=True)


def cmd_files(args: argparse.Namespace) -> int:
    """Diff two files."""
    lines1 = read_lines(args.file1)
    lines2 = read_lines(args.file2)

    if args.unified or args.format == "unified":
        diff = difflib.unified_diff(
            lines1, lines2,
            fromfile=args.file1,
            tofile=args.file2,
            n=args.context,
        )
    elif args.format == "context":
        diff = difflib.context_diff(
            lines1, lines2,
            fromfile=args.file1,
            tofile=args.file2,
            n=args.context,
        )
    elif args.format == "ndiff":
        diff = difflib.ndiff(lines1, lines2)
    else:
        diff = difflib.unified_diff(
            lines1, lines2,
            fromfile=args.file1,
            tofile=args.file2,
            n=args.context,
        )

    has_diff = False
    for line in diff:
        has_diff = True
        if args.color:
            if line.startswith("+") and not line.startswith("+++"):
                print(Terminal.colorize(line.rstrip(), color="green"))
            elif line.startswith("-") and not line.startswith("---"):
                print(Terminal.colorize(line.rstrip(), color="red"))
            elif line.startswith("@@"):
                print(Terminal.colorize(line.rstrip(), color="cyan"))
            else:
                print(line.rstrip())
        else:
            print(line, end="")

    if not has_diff:
        print(Terminal.colorize("Files are identical", color="green"))
        return 0
    return 1


def cmd_dirs(args: argparse.Namespace) -> int:
    """Diff two directories."""
    dir1 = PathLib(args.dir1)
    dir2 = PathLib(args.dir2)

    if not dir1.is_dir():
        print(Terminal.colorize(f"Not a directory: {args.dir1}", color="red"))
        return 1
    if not dir2.is_dir():
        print(Terminal.colorize(f"Not a directory: {args.dir2}", color="red"))
        return 1

    # Get file lists
    def get_files(directory: PathLib, relative_to: PathLib) -> set[str]:
        files = set()
        for root, _, filenames in os.walk(directory):
            for f in filenames:
                path = PathLib(root) / f
                rel_path = path.relative_to(relative_to)
                files.add(str(rel_path))
        return files

    files1 = get_files(dir1, dir1)
    files2 = get_files(dir2, dir2)

    only_in_1 = files1 - files2
    only_in_2 = files2 - files1
    common = files1 & files2

    has_diff = False

    # Files only in first dir
    if only_in_1:
        has_diff = True
        print(Terminal.colorize(f"\nOnly in {args.dir1}:", color="red", bold=True))
        for f in sorted(only_in_1):
            print(f"  - {f}")

    # Files only in second dir
    if only_in_2:
        has_diff = True
        print(Terminal.colorize(f"\nOnly in {args.dir2}:", color="green", bold=True))
        for f in sorted(only_in_2):
            print(f"  + {f}")

    # Diff common files
    if args.content:
        different = []
        for f in sorted(common):
            content1 = Path.read(str(dir1 / f))
            content2 = Path.read(str(dir2 / f))
            if content1 != content2:
                different.append(f)

        if different:
            has_diff = True
            print(Terminal.colorize("\nDifferent files:", color="yellow", bold=True))
            for f in different:
                print(f"  ~ {f}")

    if not has_diff:
        print(Terminal.colorize("Directories are identical", color="green"))
        return 0

    return 1


def cmd_inline(args: argparse.Namespace) -> int:
    """Show inline word-by-word diff."""
    lines1 = read_lines(args.file1)
    lines2 = read_lines(args.file2)

    matcher = difflib.SequenceMatcher(None, lines1, lines2)

    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal":
            for line in lines1[i1:i2]:
                print(line, end="")
        elif tag == "replace":
            for line in lines1[i1:i2]:
                print(Terminal.colorize(f"- {line.rstrip()}", color="red"))
            for line in lines2[j1:j2]:
                print(Terminal.colorize(f"+ {line.rstrip()}", color="green"))
        elif tag == "delete":
            for line in lines1[i1:i2]:
                print(Terminal.colorize(f"- {line.rstrip()}", color="red"))
        elif tag == "insert":
            for line in lines2[j1:j2]:
                print(Terminal.colorize(f"+ {line.rstrip()}", color="green"))

    return 0


def cmd_stats(args: argparse.Namespace) -> int:
    """Show diff statistics."""
    lines1 = read_lines(args.file1)
    lines2 = read_lines(args.file2)

    diff = list(difflib.unified_diff(lines1, lines2))

    additions = sum(1 for line in diff if line.startswith("+") and not line.startswith("+++"))
    deletions = sum(1 for line in diff if line.startswith("-") and not line.startswith("---"))

    print(f"\n{Terminal.colorize('Diff Statistics', color='cyan', bold=True)}")
    Terminal.print_line("─", width=40)
    print(f"File 1: {args.file1} ({len(lines1)} lines)")
    print(f"File 2: {args.file2} ({len(lines2)} lines)")
    print()
    print(Terminal.colorize(f"  + {additions} additions", color="green"))
    print(Terminal.colorize(f"  - {deletions} deletions", color="red"))
    print(f"  = {len(lines1) - deletions} unchanged")

    # Similarity ratio
    matcher = difflib.SequenceMatcher(None, lines1, lines2)
    similarity = matcher.ratio() * 100
    print(f"\n  Similarity: {similarity:.1f}%")

    return 0


def cmd_html(args: argparse.Namespace) -> int:
    """Generate HTML diff."""
    lines1 = read_lines(args.file1)
    lines2 = read_lines(args.file2)

    differ = difflib.HtmlDiff()
    html = differ.make_file(
        lines1, lines2,
        fromdesc=args.file1,
        todesc=args.file2,
        context=args.context > 0,
        numlines=args.context,
    )

    if args.output:
        Path.write(args.output, content=html)
        print(Terminal.colorize(f"Saved to {args.output}", color="green"))
    else:
        print(html)

    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Diff tool - compare files and directories with colored output.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Compare two files (unified diff with colors)
  python diff_tool.py files old.txt new.txt
  # Output: Shows +/- lines in green/red

  # Compare with more context lines
  python diff_tool.py files old.py new.py -c 5

  # Use different diff formats
  python diff_tool.py files old.txt new.txt -f context
  python diff_tool.py files old.txt new.txt -f ndiff

  # Disable colors (for piping to file)
  python diff_tool.py files old.txt new.txt --no-color > changes.patch

  # Compare directories (structure)
  python diff_tool.py dirs project_v1/ project_v2/
  # Output: Only in project_v1: removed.py
  #         Only in project_v2: added.py

  # Compare directories including file contents
  python diff_tool.py dirs project_v1/ project_v2/ --content

  # Inline word-by-word diff
  python diff_tool.py inline old.txt new.txt

  # Get diff statistics
  python diff_tool.py stats old.py new.py
  # Output: + 20 additions, - 5 deletions, Similarity: 87.5%%

  # Generate HTML diff report
  python diff_tool.py html old.py new.py -o diff_report.html
""",
    )
    subparsers = parser.add_subparsers(dest="command", help="Command")

    # Files diff
    p = subparsers.add_parser("files", aliases=["f"], help="Diff two files")
    p.add_argument("file1", help="First file")
    p.add_argument("file2", help="Second file")
    p.add_argument("-u", "--unified", action="store_true", help="Unified format")
    p.add_argument("-c", "--context", type=int, default=3, help="Context lines")
    p.add_argument("-f", "--format", choices=["unified", "context", "ndiff"], default="unified")
    p.add_argument("--color", action="store_true", default=True, help="Color output")
    p.add_argument("--no-color", action="store_false", dest="color")
    p.set_defaults(func=cmd_files)

    # Dirs diff
    p = subparsers.add_parser("dirs", aliases=["d"], help="Diff two directories")
    p.add_argument("dir1", help="First directory")
    p.add_argument("dir2", help="Second directory")
    p.add_argument("--content", action="store_true", help="Also compare file contents")
    p.set_defaults(func=cmd_dirs)

    # Inline diff
    p = subparsers.add_parser("inline", aliases=["i"], help="Inline word diff")
    p.add_argument("file1", help="First file")
    p.add_argument("file2", help="Second file")
    p.set_defaults(func=cmd_inline)

    # Stats
    p = subparsers.add_parser("stats", aliases=["s"], help="Diff statistics")
    p.add_argument("file1", help="First file")
    p.add_argument("file2", help="Second file")
    p.set_defaults(func=cmd_stats)

    # HTML
    p = subparsers.add_parser("html", help="Generate HTML diff")
    p.add_argument("file1", help="First file")
    p.add_argument("file2", help="Second file")
    p.add_argument("-o", "--output", help="Output file")
    p.add_argument("-c", "--context", type=int, default=3, help="Context lines")
    p.set_defaults(func=cmd_html)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 0

    try:
        return args.func(args)
    except FileNotFoundError as e:
        print(Terminal.colorize(f"File not found: {e}", color="red"), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
