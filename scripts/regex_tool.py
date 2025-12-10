#!/usr/bin/env python3
"""Test and debug regex patterns interactively."""

import argparse
import re
import sys
from pathlib import Path as PathLib

# Add parent directory to path to import utils
sys.path.insert(0, str(PathLib(__file__).parent.parent))

from utils import Path, Terminal


def highlight_matches(text: str, matches: list, color: str = "green") -> str:
    """Highlight matches in text."""
    if not matches:
        return text

    result = []
    last_end = 0

    for match in matches:
        start, end = match.span()
        result.append(text[last_end:start])
        result.append(Terminal.colorize(text[start:end], color=color, bold=True))
        last_end = end

    result.append(text[last_end:])
    return "".join(result)


def cmd_test(args: argparse.Namespace) -> int:
    """Test regex pattern against text."""
    try:
        flags = 0
        if args.ignore_case:
            flags |= re.IGNORECASE
        if args.multiline:
            flags |= re.MULTILINE
        if args.dotall:
            flags |= re.DOTALL

        pattern = re.compile(args.pattern, flags)
    except re.error as e:
        print(Terminal.colorize(f"Invalid regex: {e}", color="red"))
        return 1

    # Get text
    if args.file:
        text = Path.read(args.file)
    elif args.text:
        text = args.text
    else:
        text = sys.stdin.read()

    matches = list(pattern.finditer(text))

    print(f"\n{Terminal.colorize('Regex Test', color='cyan', bold=True)}")
    Terminal.print_line("─", width=60)
    print(f"Pattern: {Terminal.colorize(args.pattern, color='yellow')}")
    print(f"Matches: {len(matches)}")
    print()

    if matches:
        if args.show_groups:
            for i, match in enumerate(matches, 1):
                print(f"{Terminal.colorize(f'Match {i}:', color='cyan')}")
                print(f"  Full: {Terminal.colorize(match.group(), color='green')}")
                print(f"  Span: {match.span()}")
                if match.groups():
                    for j, group in enumerate(match.groups(), 1):
                        print(f"  Group {j}: {group}")
                if match.groupdict():
                    for name, value in match.groupdict().items():
                        print(f"  {name}: {value}")
                print()
        else:
            # Show highlighted text
            print(Terminal.colorize("Highlighted matches:", color="cyan"))
            print()
            highlighted = highlight_matches(text, matches)
            print(highlighted)
    else:
        print(Terminal.colorize("No matches found", color="yellow"))

    return 0


def cmd_replace(args: argparse.Namespace) -> int:
    """Replace matches with replacement string."""
    try:
        flags = 0
        if args.ignore_case:
            flags |= re.IGNORECASE
        if args.multiline:
            flags |= re.MULTILINE

        pattern = re.compile(args.pattern, flags)
    except re.error as e:
        print(Terminal.colorize(f"Invalid regex: {e}", color="red"))
        return 1

    # Get text
    if args.file:
        text = Path.read(args.file)
    elif args.text:
        text = args.text
    else:
        text = sys.stdin.read()

    result, count = pattern.subn(args.replacement, text)

    print(f"Replaced {count} matches", file=sys.stderr)

    if args.output:
        Path.write(args.output, content=result)
        print(Terminal.colorize(f"Saved to {args.output}", color="green"), file=sys.stderr)
    else:
        print(result)

    return 0


def cmd_split(args: argparse.Namespace) -> int:
    """Split text by pattern."""
    try:
        pattern = re.compile(args.pattern)
    except re.error as e:
        print(Terminal.colorize(f"Invalid regex: {e}", color="red"))
        return 1

    if args.file:
        text = Path.read(args.file)
    elif args.text:
        text = args.text
    else:
        text = sys.stdin.read()

    parts = pattern.split(text, maxsplit=args.max or 0)

    for part in parts:
        print(part)

    return 0


def cmd_extract(args: argparse.Namespace) -> int:
    """Extract all matches."""
    try:
        flags = 0
        if args.ignore_case:
            flags |= re.IGNORECASE

        pattern = re.compile(args.pattern, flags)
    except re.error as e:
        print(Terminal.colorize(f"Invalid regex: {e}", color="red"))
        return 1

    if args.file:
        text = Path.read(args.file)
    elif args.text:
        text = args.text
    else:
        text = sys.stdin.read()

    matches = pattern.findall(text)

    if args.unique:
        matches = list(dict.fromkeys(matches))

    for match in matches:
        if isinstance(match, tuple):
            print("\t".join(match))
        else:
            print(match)

    return 0


def cmd_explain(args: argparse.Namespace) -> int:
    """Explain regex pattern components."""
    pattern = args.pattern

    print(f"\n{Terminal.colorize('Regex Explanation', color='cyan', bold=True)}")
    Terminal.print_line("─", width=60)
    print(f"Pattern: {Terminal.colorize(pattern, color='yellow')}")
    print()

    # Common regex components
    explanations = {
        r".": "Any character except newline",
        r"^": "Start of string/line",
        r"$": "End of string/line",
        r"*": "Zero or more of previous",
        r"+": "One or more of previous",
        r"?": "Zero or one of previous (optional)",
        r"\d": "Digit [0-9]",
        r"\D": "Non-digit",
        r"\w": "Word character [a-zA-Z0-9_]",
        r"\W": "Non-word character",
        r"\s": "Whitespace",
        r"\S": "Non-whitespace",
        r"\b": "Word boundary",
        r"\B": "Non-word boundary",
        r"[": "Character class start",
        r"]": "Character class end",
        r"(": "Capture group start",
        r")": "Capture group end",
        r"|": "Alternation (or)",
        r"{n}": "Exactly n times",
        r"{n,}": "n or more times",
        r"{n,m}": "Between n and m times",
        r"(?:": "Non-capturing group",
        r"(?=": "Positive lookahead",
        r"(?!": "Negative lookahead",
        r"(?<=": "Positive lookbehind",
        r"(?<!": "Negative lookbehind",
        r"(?P<name>": "Named capture group",
    }

    print(Terminal.colorize("Components found:", color="cyan"))
    found = []
    for component, explanation in explanations.items():
        if component in pattern:
            found.append((component, explanation))

    if found:
        max_len = max(len(c) for c, _ in found)
        for component, explanation in found:
            print(f"  {Terminal.colorize(component.ljust(max_len + 2), color='yellow')}{explanation}")
    else:
        print("  No special components found (literal string)")

    # Try to validate
    try:
        re.compile(pattern)
        print(f"\n{Terminal.colorize('✓ Pattern is valid', color='green')}")
    except re.error as e:
        print(f"\n{Terminal.colorize(f'✗ Pattern error: {e}', color='red')}")

    return 0


def cmd_interactive(args: argparse.Namespace) -> int:
    """Interactive regex testing."""
    print(Terminal.colorize("Interactive Regex Tester", color="cyan", bold=True))
    print("Enter pattern and text to test. Type 'quit' to exit.")
    Terminal.print_line("─", width=60)

    while True:
        try:
            pattern_str = input(Terminal.colorize("\nPattern: ", color="cyan"))
            if pattern_str.lower() in ("quit", "exit", "q"):
                break

            try:
                pattern = re.compile(pattern_str)
            except re.error as e:
                print(Terminal.colorize(f"Invalid regex: {e}", color="red"))
                continue

            text = input(Terminal.colorize("Text: ", color="cyan"))

            matches = list(pattern.finditer(text))
            print(f"\nMatches: {len(matches)}")

            if matches:
                highlighted = highlight_matches(text, matches)
                print(f"Result: {highlighted}")

                for i, match in enumerate(matches, 1):
                    print(f"\n  Match {i}: '{match.group()}' at {match.span()}")
                    if match.groups():
                        for j, group in enumerate(match.groups(), 1):
                            print(f"    Group {j}: {group}")
            else:
                print(Terminal.colorize("No matches", color="yellow"))

        except (KeyboardInterrupt, EOFError):
            break

    print("\nGoodbye!")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Regex tool - test, debug, and explain regular expressions.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Test pattern against text (shows highlighted matches)
  python regex_tool.py test "\\d+" "Order 12345 received"
  # Output: Pattern: \\d+, Matches: 1
  #         Order [12345] received (highlighted)

  # Test with capture groups
  python regex_tool.py test "(\\w+)@(\\w+\\.\\w+)" "email@example.com" -g
  # Output: Match 1: email@example.com
  #         Group 1: email
  #         Group 2: example.com

  # Test with file input
  python regex_tool.py test "TODO.*" -f source.py

  # Case-insensitive matching
  python regex_tool.py test "error" logfile.txt -i

  # Multiline mode (^ and $ match line boundaries)
  python regex_tool.py test "^import.*" -f script.py -m

  # Replace matches
  python regex_tool.py replace "\\d{4}-\\d{4}" "XXXX-XXXX" "Card: 1234-5678"
  # Output: Card: XXXX-XXXX

  # Replace with backreferences
  python regex_tool.py replace "(\\w+), (\\w+)" "\\2 \\1" "Doe, John"
  # Output: John Doe

  # Replace in file and save
  python regex_tool.py replace "TODO" "DONE" -f tasks.txt -o updated.txt

  # Split text by pattern
  python regex_tool.py split "[,;\\s]+" "a, b; c d"
  # Output: a\\nb\\nc\\nd

  # Extract all matches
  python regex_tool.py extract "[\\w.]+@[\\w.]+" -f emails.txt
  # Outputs each email on a line

  # Extract unique matches only
  python regex_tool.py extract "https?://[^\\s]+" -f page.html -u

  # Explain pattern components
  python regex_tool.py explain "^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\\.[a-zA-Z0-9-.]+$"
  # Output: Components found: ^, [], +, @, \\., $

  # Interactive regex testing
  python regex_tool.py interactive
  # Pattern: \\d+
  # Text: abc123def
  # Matches: 1, Result: abc[123]def
""",
    )
    subparsers = parser.add_subparsers(dest="command", help="Command")

    # Test
    p = subparsers.add_parser("test", aliases=["t"], help="Test pattern")
    p.add_argument("pattern", help="Regex pattern")
    p.add_argument("text", nargs="?", help="Text to match")
    p.add_argument("-f", "--file", help="Read text from file")
    p.add_argument("-i", "--ignore-case", action="store_true")
    p.add_argument("-m", "--multiline", action="store_true")
    p.add_argument("-s", "--dotall", action="store_true", help=". matches newline")
    p.add_argument("-g", "--show-groups", action="store_true", help="Show capture groups")
    p.set_defaults(func=cmd_test)

    # Replace
    p = subparsers.add_parser("replace", aliases=["r", "sub"], help="Replace matches")
    p.add_argument("pattern", help="Regex pattern")
    p.add_argument("replacement", help="Replacement string")
    p.add_argument("text", nargs="?", help="Text to process")
    p.add_argument("-f", "--file", help="Read text from file")
    p.add_argument("-o", "--output", help="Output file")
    p.add_argument("-i", "--ignore-case", action="store_true")
    p.add_argument("-m", "--multiline", action="store_true")
    p.set_defaults(func=cmd_replace)

    # Split
    p = subparsers.add_parser("split", help="Split by pattern")
    p.add_argument("pattern", help="Regex pattern")
    p.add_argument("text", nargs="?", help="Text to split")
    p.add_argument("-f", "--file", help="Read text from file")
    p.add_argument("--max", type=int, help="Maximum splits")
    p.set_defaults(func=cmd_split)

    # Extract
    p = subparsers.add_parser("extract", aliases=["e"], help="Extract matches")
    p.add_argument("pattern", help="Regex pattern")
    p.add_argument("text", nargs="?", help="Text to search")
    p.add_argument("-f", "--file", help="Read text from file")
    p.add_argument("-i", "--ignore-case", action="store_true")
    p.add_argument("-u", "--unique", action="store_true", help="Unique matches only")
    p.set_defaults(func=cmd_extract)

    # Explain
    p = subparsers.add_parser("explain", aliases=["x"], help="Explain pattern")
    p.add_argument("pattern", help="Regex pattern")
    p.set_defaults(func=cmd_explain)

    # Interactive
    p = subparsers.add_parser("interactive", aliases=["i"], help="Interactive mode")
    p.set_defaults(func=cmd_interactive)

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
