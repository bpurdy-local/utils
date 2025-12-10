#!/usr/bin/env python3
"""Text processing - find/replace, extract, transform."""

import argparse
import re
import sys
from pathlib import Path as PathLib

# Add parent directory to path to import utils
sys.path.insert(0, str(PathLib(__file__).parent.parent))

from utils import Path, String, Terminal


def read_input(file_path: str | None) -> str:
    """Read input from file or stdin."""
    if file_path:
        return Path.read(file_path)
    return sys.stdin.read()


def write_output(data: str, output: str | None) -> None:
    """Write output to file or stdout."""
    if output:
        Path.write(output, content=data)
        print(Terminal.colorize(f"Written to {output}", color="green"), file=sys.stderr)
    else:
        print(data, end="")


def cmd_replace(args: argparse.Namespace) -> int:
    """Find and replace text."""
    text = read_input(args.file)

    if args.regex:
        flags = re.IGNORECASE if args.ignore_case else 0
        result = re.sub(args.find, args.replace, text, flags=flags)
    else:
        if args.ignore_case:
            pattern = re.compile(re.escape(args.find), re.IGNORECASE)
            result = pattern.sub(args.replace, text)
        else:
            result = text.replace(args.find, args.replace)

    write_output(result, args.output)
    return 0


def cmd_extract(args: argparse.Namespace) -> int:
    """Extract matching patterns."""
    text = read_input(args.file)

    flags = re.IGNORECASE if args.ignore_case else 0
    matches = re.findall(args.pattern, text, flags=flags)

    if args.unique:
        matches = list(dict.fromkeys(matches))

    for match in matches:
        if isinstance(match, tuple):
            print("\t".join(match))
        else:
            print(match)
    return 0


def cmd_lines(args: argparse.Namespace) -> int:
    """Filter lines."""
    text = read_input(args.file)
    lines = text.splitlines()

    if args.contains:
        if args.ignore_case:
            lines = [l for l in lines if args.contains.lower() in l.lower()]
        else:
            lines = [l for l in lines if args.contains in l]
    elif args.regex:
        flags = re.IGNORECASE if args.ignore_case else 0
        pattern = re.compile(args.regex, flags)
        lines = [l for l in lines if pattern.search(l)]
    elif args.startswith:
        lines = [l for l in lines if l.startswith(args.startswith)]
    elif args.endswith:
        lines = [l for l in lines if l.endswith(args.endswith)]

    if args.invert:
        all_lines = text.splitlines()
        lines = [l for l in all_lines if l not in lines]

    if args.number:
        lines = [f"{i+1}: {l}" for i, l in enumerate(lines)]

    write_output("\n".join(lines) + "\n" if lines else "", args.output)
    return 0


def cmd_case(args: argparse.Namespace) -> int:
    """Transform text case."""
    text = read_input(args.file)

    if args.transform == "upper":
        result = text.upper()
    elif args.transform == "lower":
        result = text.lower()
    elif args.transform == "title":
        result = text.title()
    elif args.transform == "sentence":
        result = ". ".join(s.capitalize() for s in text.split(". "))
    elif args.transform == "camel":
        result = String.to_camel(text.replace(" ", "_").replace("-", "_"))
    elif args.transform == "snake":
        result = String.to_snake(text)
    elif args.transform == "kebab":
        result = String.to_kebab(text)
    elif args.transform == "pascal":
        result = String.to_pascal(text.replace(" ", "_").replace("-", "_"))
    else:
        result = text

    write_output(result, args.output)
    return 0


def cmd_trim(args: argparse.Namespace) -> int:
    """Trim whitespace."""
    text = read_input(args.file)

    if args.lines:
        lines = text.splitlines()
        if args.left:
            lines = [l.lstrip() for l in lines]
        elif args.right:
            lines = [l.rstrip() for l in lines]
        else:
            lines = [l.strip() for l in lines]
        result = "\n".join(lines)
    else:
        if args.left:
            result = text.lstrip()
        elif args.right:
            result = text.rstrip()
        else:
            result = text.strip()

    write_output(result, args.output)
    return 0


def cmd_count(args: argparse.Namespace) -> int:
    """Count occurrences."""
    text = read_input(args.file)

    if args.pattern:
        flags = re.IGNORECASE if args.ignore_case else 0
        count = len(re.findall(args.pattern, text, flags=flags))
        print(f"Pattern matches: {count}")
    else:
        lines = text.splitlines()
        words = text.split()
        chars = len(text)
        chars_no_space = len(text.replace(" ", "").replace("\n", ""))

        print(f"Lines: {len(lines)}")
        print(f"Words: {len(words)}")
        print(f"Characters: {chars}")
        print(f"Characters (no whitespace): {chars_no_space}")

    return 0


def cmd_wrap(args: argparse.Namespace) -> int:
    """Wrap text at specified width."""
    text = read_input(args.file)
    result = String.wrap(text, width=args.width)
    write_output(result, args.output)
    return 0


def cmd_truncate(args: argparse.Namespace) -> int:
    """Truncate text."""
    text = read_input(args.file)

    if args.lines:
        lines = text.splitlines()
        result = "\n".join(lines[: args.length])
    else:
        result = String.truncate(text, length=args.length, suffix=args.suffix)

    write_output(result, args.output)
    return 0


def cmd_split(args: argparse.Namespace) -> int:
    """Split text by delimiter."""
    text = read_input(args.file).strip()

    if args.regex:
        parts = re.split(args.delimiter, text)
    else:
        parts = text.split(args.delimiter)

    for part in parts:
        print(part)
    return 0


def cmd_join(args: argparse.Namespace) -> int:
    """Join lines with delimiter."""
    text = read_input(args.file)
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    result = args.delimiter.join(lines)
    write_output(result + "\n", args.output)
    return 0


def cmd_reverse(args: argparse.Namespace) -> int:
    """Reverse text or lines."""
    text = read_input(args.file)

    if args.lines:
        lines = text.splitlines()
        result = "\n".join(reversed(lines))
    else:
        result = text[::-1]

    write_output(result, args.output)
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Text processing tool - find/replace, extract, transform, filter.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Find and replace text
  python text_tool.py replace "foo" "bar" file.txt
  python text_tool.py replace "old" "new" file.txt -o output.txt
  # Input:  Hello foo world
  # Output: Hello bar world

  # Regex replace (use -r flag)
  python text_tool.py replace "\\d+" "NUM" file.txt -r
  # Input:  Order 12345 received
  # Output: Order NUM received

  # Case-insensitive replace
  python text_tool.py replace "hello" "hi" file.txt -i

  # Extract patterns with regex
  python text_tool.py extract "[\\w.]+@[\\w.]+" emails.txt
  python text_tool.py extract "\\d{3}-\\d{4}" phones.txt --unique
  # Output: Lists all matching patterns

  # Filter lines containing text
  python text_tool.py lines -c "error" logfile.txt
  python text_tool.py lines -r "ERROR|WARN" logfile.txt
  python text_tool.py lines -c "TODO" src.py -n  # with line numbers

  # Invert match (lines NOT containing)
  python text_tool.py lines -c "debug" log.txt -v

  # Transform case
  python text_tool.py case upper file.txt
  python text_tool.py case lower file.txt
  python text_tool.py case title file.txt
  # Input:  hello world
  # Output: Hello World

  # Convert to camelCase/snake_case
  echo "hello world" | python text_tool.py case camel
  # Output: helloWorld
  echo "helloWorld" | python text_tool.py case snake
  # Output: hello_world

  # Trim whitespace
  python text_tool.py trim file.txt
  python text_tool.py trim file.txt --lines  # trim each line

  # Word/line count
  python text_tool.py count file.txt
  # Output: Lines: 100, Words: 500, Characters: 3000

  # Count pattern occurrences
  python text_tool.py count file.txt -p "TODO"
  # Output: Pattern matches: 15

  # Wrap text at width
  python text_tool.py wrap file.txt -w 80

  # Split by delimiter
  echo "a,b,c" | python text_tool.py split ","
  # Output: a\\nb\\nc

  # Join lines with delimiter
  python text_tool.py join file.txt -d ", "
  # Input:  a\\nb\\nc
  # Output: a, b, c
""",
    )
    subparsers = parser.add_subparsers(dest="command", help="command to run")

    # Replace
    p = subparsers.add_parser("replace", aliases=["sub"], help="Find and replace")
    p.add_argument("find", help="Text to find")
    p.add_argument("replace", help="Replacement text")
    p.add_argument("file", nargs="?", help="Input file")
    p.add_argument("-r", "--regex", action="store_true", help="Use regex")
    p.add_argument("-i", "--ignore-case", action="store_true", help="Case insensitive")
    p.add_argument("-o", "--output", help="Output file")
    p.set_defaults(func=cmd_replace)

    # Extract
    p = subparsers.add_parser("extract", help="Extract patterns")
    p.add_argument("pattern", help="Regex pattern")
    p.add_argument("file", nargs="?", help="Input file")
    p.add_argument("-i", "--ignore-case", action="store_true", help="Case insensitive")
    p.add_argument("-u", "--unique", action="store_true", help="Unique matches only")
    p.set_defaults(func=cmd_extract)

    # Lines
    p = subparsers.add_parser("lines", aliases=["grep"], help="Filter lines")
    p.add_argument("file", nargs="?", help="Input file")
    p.add_argument("-c", "--contains", help="Lines containing text")
    p.add_argument("-r", "--regex", help="Lines matching regex")
    p.add_argument("-s", "--startswith", help="Lines starting with")
    p.add_argument("-e", "--endswith", help="Lines ending with")
    p.add_argument("-v", "--invert", action="store_true", help="Invert match")
    p.add_argument("-i", "--ignore-case", action="store_true", help="Case insensitive")
    p.add_argument("-n", "--number", action="store_true", help="Show line numbers")
    p.add_argument("-o", "--output", help="Output file")
    p.set_defaults(func=cmd_lines)

    # Case
    p = subparsers.add_parser("case", help="Transform case")
    p.add_argument(
        "transform",
        choices=["upper", "lower", "title", "sentence", "camel", "snake", "kebab", "pascal"],
        help="Transform type",
    )
    p.add_argument("file", nargs="?", help="Input file")
    p.add_argument("-o", "--output", help="Output file")
    p.set_defaults(func=cmd_case)

    # Trim
    p = subparsers.add_parser("trim", help="Trim whitespace")
    p.add_argument("file", nargs="?", help="Input file")
    p.add_argument("-l", "--left", action="store_true", help="Left trim only")
    p.add_argument("-r", "--right", action="store_true", help="Right trim only")
    p.add_argument("--lines", action="store_true", help="Trim each line")
    p.add_argument("-o", "--output", help="Output file")
    p.set_defaults(func=cmd_trim)

    # Count
    p = subparsers.add_parser("count", aliases=["wc"], help="Count occurrences")
    p.add_argument("file", nargs="?", help="Input file")
    p.add_argument("-p", "--pattern", help="Regex pattern to count")
    p.add_argument("-i", "--ignore-case", action="store_true", help="Case insensitive")
    p.set_defaults(func=cmd_count)

    # Wrap
    p = subparsers.add_parser("wrap", help="Wrap text")
    p.add_argument("file", nargs="?", help="Input file")
    p.add_argument("-w", "--width", type=int, default=80, help="Wrap width (default: 80)")
    p.add_argument("-o", "--output", help="Output file")
    p.set_defaults(func=cmd_wrap)

    # Truncate
    p = subparsers.add_parser("truncate", aliases=["trunc"], help="Truncate text")
    p.add_argument("length", type=int, help="Max length")
    p.add_argument("file", nargs="?", help="Input file")
    p.add_argument("--suffix", default="...", help="Suffix (default: ...)")
    p.add_argument("--lines", action="store_true", help="Truncate by lines")
    p.add_argument("-o", "--output", help="Output file")
    p.set_defaults(func=cmd_truncate)

    # Split
    p = subparsers.add_parser("split", help="Split by delimiter")
    p.add_argument("delimiter", help="Delimiter")
    p.add_argument("file", nargs="?", help="Input file")
    p.add_argument("-r", "--regex", action="store_true", help="Regex delimiter")
    p.set_defaults(func=cmd_split)

    # Join
    p = subparsers.add_parser("join", help="Join lines")
    p.add_argument("file", nargs="?", help="Input file")
    p.add_argument("-d", "--delimiter", default=" ", help="Delimiter (default: space)")
    p.add_argument("-o", "--output", help="Output file")
    p.set_defaults(func=cmd_join)

    # Reverse
    p = subparsers.add_parser("reverse", aliases=["rev"], help="Reverse text")
    p.add_argument("file", nargs="?", help="Input file")
    p.add_argument("--lines", action="store_true", help="Reverse line order")
    p.add_argument("-o", "--output", help="Output file")
    p.set_defaults(func=cmd_reverse)

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
