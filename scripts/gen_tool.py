#!/usr/bin/env python3
"""Generate data - UUIDs, passwords, random strings, timestamps."""

import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path as PathLib

# Add parent directory to path to import utils
sys.path.insert(0, str(PathLib(__file__).parent.parent))

from utils import Datetime, Random, Terminal


def cmd_uuid(args: argparse.Namespace) -> int:
    """Generate UUIDs."""
    for _ in range(args.count):
        uuid = Random.uuid()
        if args.upper:
            uuid = uuid.upper()
        print(uuid)
    return 0


def cmd_password(args: argparse.Namespace) -> int:
    """Generate passwords."""
    for _ in range(args.count):
        password = Random.password(
            length=args.length,
            uppercase=not args.no_upper,
            lowercase=not args.no_lower,
            digits=not args.no_digits,
            special=not args.no_special,
        )
        print(password)
    return 0


def cmd_string(args: argparse.Namespace) -> int:
    """Generate random strings."""
    charset = ""
    if args.alpha:
        charset += "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    if args.digits:
        charset += "0123456789"
    if args.hex:
        charset = "0123456789abcdef"
    if args.chars:
        charset = args.chars

    if not charset:
        charset = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"

    for _ in range(args.count):
        result = "".join(Random.choice(list(charset)) for _ in range(args.length))
        print(result)
    return 0


def cmd_hex(args: argparse.Namespace) -> int:
    """Generate hex strings."""
    for _ in range(args.count):
        result = Random.hex(length=args.length)
        if args.upper:
            result = result.upper()
        print(result)
    return 0


def cmd_int(args: argparse.Namespace) -> int:
    """Generate random integers."""
    for _ in range(args.count):
        print(Random.int(min_val=args.min, max_val=args.max))
    return 0


def cmd_float(args: argparse.Namespace) -> int:
    """Generate random floats."""
    for _ in range(args.count):
        val = Random.float(min_val=args.min, max_val=args.max)
        print(f"{val:.{args.precision}f}")
    return 0


def cmd_timestamp(args: argparse.Namespace) -> int:
    """Generate timestamps."""
    now = datetime.now(timezone.utc)

    if args.format == "iso":
        print(now.isoformat())
    elif args.format == "unix":
        print(int(now.timestamp()))
    elif args.format == "unix_ms":
        print(int(now.timestamp() * 1000))
    elif args.format == "date":
        print(now.strftime("%Y-%m-%d"))
    elif args.format == "time":
        print(now.strftime("%H:%M:%S"))
    elif args.format == "datetime":
        print(now.strftime("%Y-%m-%d %H:%M:%S"))
    elif args.format == "rfc2822":
        print(now.strftime("%a, %d %b %Y %H:%M:%S +0000"))
    elif args.custom:
        print(now.strftime(args.custom))
    else:
        print(now.isoformat())
    return 0


def cmd_date(args: argparse.Namespace) -> int:
    """Generate dates."""
    if args.random:
        # Random date in range
        start = Datetime.parse(args.start) if args.start else datetime(2000, 1, 1)
        end = Datetime.parse(args.end) if args.end else datetime.now()

        import random as rand_mod

        for _ in range(args.count):
            timestamp = rand_mod.uniform(start.timestamp(), end.timestamp())
            dt = datetime.fromtimestamp(timestamp)
            print(Datetime.format(dt, fmt=args.format))
    else:
        now = datetime.now()
        print(Datetime.format(now, fmt=args.format))
    return 0


def cmd_choice(args: argparse.Namespace) -> int:
    """Pick random choice from options."""
    for _ in range(args.count):
        print(Random.choice(args.options))
    return 0


def cmd_shuffle(args: argparse.Namespace) -> int:
    """Shuffle input lines."""
    if args.file:
        from utils import Path

        lines = Path.read(args.file).splitlines()
    else:
        lines = sys.stdin.read().splitlines()

    shuffled = Random.shuffle(lines)
    for line in shuffled:
        print(line)
    return 0


def cmd_sample(args: argparse.Namespace) -> int:
    """Sample N items from input."""
    if args.file:
        from utils import Path

        lines = Path.read(args.file).splitlines()
    else:
        lines = sys.stdin.read().splitlines()

    sampled = Random.sample(lines, count=min(args.n, len(lines)))
    for line in sampled:
        print(line)
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Data generation tool - UUIDs, passwords, random strings, timestamps.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate UUIDs
  python gen_tool.py uuid
  # Output: 7f3b8c9a-4d5e-4f6a-8b9c-0d1e2f3a4b5c

  python gen_tool.py uuid -c 5
  # Output: (5 UUIDs, one per line)

  python gen_tool.py uuid -u
  # Output: 7F3B8C9A-4D5E-4F6A-8B9C-0D1E2F3A4B5C

  # Generate passwords
  python gen_tool.py password
  # Output: Kj8#mP2$nQ5@xL9& (16 chars with all character types)

  python gen_tool.py password -l 24
  # Output: (24-character password)

  python gen_tool.py password --no-special
  # Output: Kj8mP2nQ5xL9vBcD (no special characters)

  python gen_tool.py pw -c 5
  # Output: (5 passwords, one per line)

  # Generate random strings
  python gen_tool.py string -l 8
  # Output: xK9mPq2n (alphanumeric)

  python gen_tool.py string --alpha
  # Output: xKmPqnRt (letters only)

  python gen_tool.py string --digits -l 6
  # Output: 847293 (digits only)

  python gen_tool.py string --hex -l 16
  # Output: a7f3b9c2d4e5f6a8

  python gen_tool.py string --chars "ACGT" -l 20
  # Output: ACGTTAGCAGTCGATCAGTA (DNA sequence)

  # Generate hex strings
  python gen_tool.py hex
  # Output: a7f3b9c2d4e5f6a81234567890abcdef (32 chars)

  python gen_tool.py hex -l 16 -u
  # Output: A7F3B9C2D4E5F6A8

  # Generate random integers
  python gen_tool.py int
  # Output: 42 (0-100 range)

  python gen_tool.py int --min 1 --max 6
  # Output: 4 (dice roll)

  python gen_tool.py int --min 1 --max 100 -c 10
  # Output: (10 random numbers)

  # Generate random floats
  python gen_tool.py float
  # Output: 0.73 (0.0-1.0 range)

  python gen_tool.py float --min 0 --max 100 -p 4
  # Output: 42.7831 (4 decimal places)

  # Generate timestamps
  python gen_tool.py timestamp
  # Output: 2024-01-15T10:30:45.123456+00:00

  python gen_tool.py ts -f unix
  # Output: 1705315845

  python gen_tool.py ts -f unix_ms
  # Output: 1705315845123

  python gen_tool.py ts -f date
  # Output: 2024-01-15

  python gen_tool.py ts --custom "%%Y%%m%%d_%%H%%M%%S"
  # Output: 20240115_103045

  # Generate dates
  python gen_tool.py date
  # Output: 2024-01-15

  python gen_tool.py date -f "%%B %%d, %%Y"
  # Output: January 15, 2024

  python gen_tool.py date -r --start "2020-01-01" --end "2024-12-31" -c 5
  # Output: (5 random dates in range)

  # Pick random choice
  python gen_tool.py choice red green blue
  # Output: green

  python gen_tool.py choice heads tails -c 10
  # Output: (10 coin flips)

  # Shuffle lines
  cat names.txt | python gen_tool.py shuffle
  # Output: (shuffled lines from stdin)

  python gen_tool.py shuffle names.txt
  # Output: (shuffled lines from file)

  # Sample N random lines
  python gen_tool.py sample -n 5 data.txt
  # Output: (5 random lines from file)

  cat urls.txt | python gen_tool.py sample -n 10
  # Output: (10 random lines from stdin)
""",
    )
    subparsers = parser.add_subparsers(dest="command", help="Command")

    # UUID
    p = subparsers.add_parser("uuid", help="Generate UUIDs")
    p.add_argument("-c", "--count", type=int, default=1, help="Number to generate")
    p.add_argument("-u", "--upper", action="store_true", help="Uppercase")
    p.set_defaults(func=cmd_uuid)

    # Password
    p = subparsers.add_parser("password", aliases=["pw", "pass"], help="Generate passwords")
    p.add_argument("-l", "--length", type=int, default=16, help="Length (default: 16)")
    p.add_argument("-c", "--count", type=int, default=1, help="Number to generate")
    p.add_argument("--no-upper", action="store_true", help="No uppercase")
    p.add_argument("--no-lower", action="store_true", help="No lowercase")
    p.add_argument("--no-digits", action="store_true", help="No digits")
    p.add_argument("--no-special", action="store_true", help="No special chars")
    p.set_defaults(func=cmd_password)

    # String
    p = subparsers.add_parser("string", aliases=["str"], help="Generate random strings")
    p.add_argument("-l", "--length", type=int, default=16, help="Length (default: 16)")
    p.add_argument("-c", "--count", type=int, default=1, help="Number to generate")
    p.add_argument("--alpha", action="store_true", help="Letters only")
    p.add_argument("--digits", action="store_true", help="Digits only")
    p.add_argument("--hex", action="store_true", help="Hex chars only")
    p.add_argument("--chars", help="Custom character set")
    p.set_defaults(func=cmd_string)

    # Hex
    p = subparsers.add_parser("hex", help="Generate hex strings")
    p.add_argument("-l", "--length", type=int, default=32, help="Length (default: 32)")
    p.add_argument("-c", "--count", type=int, default=1, help="Number to generate")
    p.add_argument("-u", "--upper", action="store_true", help="Uppercase")
    p.set_defaults(func=cmd_hex)

    # Int
    p = subparsers.add_parser("int", help="Generate random integers")
    p.add_argument("--min", type=int, default=0, help="Minimum (default: 0)")
    p.add_argument("--max", type=int, default=100, help="Maximum (default: 100)")
    p.add_argument("-c", "--count", type=int, default=1, help="Number to generate")
    p.set_defaults(func=cmd_int)

    # Float
    p = subparsers.add_parser("float", help="Generate random floats")
    p.add_argument("--min", type=float, default=0.0, help="Minimum (default: 0.0)")
    p.add_argument("--max", type=float, default=1.0, help="Maximum (default: 1.0)")
    p.add_argument("-p", "--precision", type=int, default=2, help="Decimal places (default: 2)")
    p.add_argument("-c", "--count", type=int, default=1, help="Number to generate")
    p.set_defaults(func=cmd_float)

    # Timestamp
    p = subparsers.add_parser("timestamp", aliases=["ts"], help="Generate timestamps")
    p.add_argument(
        "-f",
        "--format",
        choices=["iso", "unix", "unix_ms", "date", "time", "datetime", "rfc2822"],
        default="iso",
        help="Format (default: iso)",
    )
    p.add_argument("--custom", help="Custom strftime format")
    p.set_defaults(func=cmd_timestamp)

    # Date
    p = subparsers.add_parser("date", help="Generate dates")
    p.add_argument("-f", "--format", default="%Y-%m-%d", help="strftime format")
    p.add_argument("-r", "--random", action="store_true", help="Random date")
    p.add_argument("--start", help="Range start (for random)")
    p.add_argument("--end", help="Range end (for random)")
    p.add_argument("-c", "--count", type=int, default=1, help="Number to generate")
    p.set_defaults(func=cmd_date)

    # Choice
    p = subparsers.add_parser("choice", aliases=["pick"], help="Pick random from options")
    p.add_argument("options", nargs="+", help="Options to choose from")
    p.add_argument("-c", "--count", type=int, default=1, help="Number to pick")
    p.set_defaults(func=cmd_choice)

    # Shuffle
    p = subparsers.add_parser("shuffle", help="Shuffle lines")
    p.add_argument("file", nargs="?", help="Input file (stdin if omitted)")
    p.set_defaults(func=cmd_shuffle)

    # Sample
    p = subparsers.add_parser("sample", help="Sample N lines")
    p.add_argument("-n", type=int, default=10, help="Number to sample (default: 10)")
    p.add_argument("file", nargs="?", help="Input file (stdin if omitted)")
    p.set_defaults(func=cmd_sample)

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
