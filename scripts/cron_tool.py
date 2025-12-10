#!/usr/bin/env python3
"""Cron expression utilities - parse, explain, next run times."""

import argparse
import sys
from datetime import datetime, timedelta
from pathlib import Path as PathLib

# Add parent directory to path to import utils
sys.path.insert(0, str(PathLib(__file__).parent.parent))

from utils import Terminal


# Field definitions
FIELD_NAMES = ["minute", "hour", "day", "month", "weekday"]
FIELD_RANGES = [
    (0, 59),   # minute
    (0, 23),   # hour
    (1, 31),   # day of month
    (1, 12),   # month
    (0, 6),    # day of week (0 = Sunday)
]

MONTH_NAMES = {
    "jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
    "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12,
}

DAY_NAMES = {
    "sun": 0, "mon": 1, "tue": 2, "wed": 3, "thu": 4, "fri": 5, "sat": 6,
}


def parse_field(field: str, min_val: int, max_val: int, names: dict | None = None) -> set[int]:
    """Parse a single cron field into a set of values."""
    result = set()

    # Replace names with numbers
    if names:
        for name, num in names.items():
            field = field.lower().replace(name, str(num))

    for part in field.split(","):
        if "/" in part:
            # Handle step values
            range_part, step = part.split("/")
            step = int(step)

            if range_part == "*":
                values = range(min_val, max_val + 1, step)
            elif "-" in range_part:
                start, end = map(int, range_part.split("-"))
                values = range(start, end + 1, step)
            else:
                start = int(range_part)
                values = range(start, max_val + 1, step)

            result.update(values)

        elif "-" in part:
            # Handle ranges
            start, end = map(int, part.split("-"))
            result.update(range(start, end + 1))

        elif part == "*":
            # All values
            result.update(range(min_val, max_val + 1))

        else:
            # Single value
            result.add(int(part))

    return result


def parse_cron(expression: str) -> list[set[int]]:
    """Parse cron expression into list of value sets for each field."""
    parts = expression.split()

    # Handle special expressions
    special = {
        "@yearly": "0 0 1 1 *",
        "@annually": "0 0 1 1 *",
        "@monthly": "0 0 1 * *",
        "@weekly": "0 0 * * 0",
        "@daily": "0 0 * * *",
        "@midnight": "0 0 * * *",
        "@hourly": "0 * * * *",
    }

    if expression.lower() in special:
        parts = special[expression.lower()].split()

    if len(parts) != 5:
        raise ValueError(f"Invalid cron expression: expected 5 fields, got {len(parts)}")

    names_map = [None, None, None, MONTH_NAMES, DAY_NAMES]

    return [
        parse_field(parts[i], FIELD_RANGES[i][0], FIELD_RANGES[i][1], names_map[i])
        for i in range(5)
    ]


def matches(dt: datetime, fields: list[set[int]]) -> bool:
    """Check if datetime matches cron expression."""
    minute, hour, day, month, weekday = fields

    return (
        dt.minute in minute
        and dt.hour in hour
        and dt.day in day
        and dt.month in month
        and dt.weekday() in weekday  # Python: Monday=0, cron: Sunday=0
    )


def next_run(fields: list[set[int]], start: datetime | None = None, count: int = 1) -> list[datetime]:
    """Find next run time(s) for cron expression."""
    if start is None:
        start = datetime.now()

    # Start from next minute
    current = start.replace(second=0, microsecond=0) + timedelta(minutes=1)

    results = []
    max_iterations = 366 * 24 * 60  # Max 1 year of minutes

    for _ in range(max_iterations):
        if matches(current, fields):
            results.append(current)
            if len(results) >= count:
                break
        current += timedelta(minutes=1)

    return results


def explain_field(field: str, name: str, min_val: int, max_val: int) -> str:
    """Generate human-readable explanation for a field."""
    if field == "*":
        return f"every {name}"

    if "/" in field:
        if field.startswith("*/"):
            step = field[2:]
            return f"every {step} {name}s"
        else:
            return f"{name}: {field}"

    if "-" in field:
        start, end = field.split("-")
        return f"{name}s {start} through {end}"

    if "," in field:
        return f"{name}s: {field}"

    return f"{name} {field}"


def cmd_explain(args: argparse.Namespace) -> int:
    """Explain a cron expression."""
    try:
        parts = args.expression.split()

        # Handle special expressions
        special = {
            "@yearly": ("0 0 1 1 *", "Once a year, at midnight on January 1st"),
            "@annually": ("0 0 1 1 *", "Once a year, at midnight on January 1st"),
            "@monthly": ("0 0 1 * *", "Once a month, at midnight on the 1st"),
            "@weekly": ("0 0 * * 0", "Once a week, at midnight on Sunday"),
            "@daily": ("0 0 * * *", "Once a day, at midnight"),
            "@midnight": ("0 0 * * *", "Once a day, at midnight"),
            "@hourly": ("0 * * * *", "Once an hour, at the beginning of the hour"),
        }

        if args.expression.lower() in special:
            expanded, description = special[args.expression.lower()]
            print(f"\n{Terminal.colorize('Cron Expression', color='cyan', bold=True)}")
            Terminal.print_line("─", width=50)
            print(f"Expression: {args.expression}")
            print(f"Expanded:   {expanded}")
            print(f"\n{Terminal.colorize(description, color='green')}")
            return 0

        if len(parts) != 5:
            print(Terminal.colorize(f"Invalid: expected 5 fields, got {len(parts)}", color="red"))
            return 1

        print(f"\n{Terminal.colorize('Cron Expression', color='cyan', bold=True)}")
        Terminal.print_line("─", width=50)
        print(f"Expression: {args.expression}")
        print()

        # Explain each field
        field_labels = [
            ("Minute", 0, 59),
            ("Hour", 0, 23),
            ("Day of Month", 1, 31),
            ("Month", 1, 12),
            ("Day of Week", 0, 6),
        ]

        for i, (label, min_val, max_val) in enumerate(field_labels):
            explanation = explain_field(parts[i], label.lower(), min_val, max_val)
            print(f"  {Terminal.colorize(label + ':', color='cyan'):20} {parts[i]:10} ({explanation})")

        # Parse and show next runs
        fields = parse_cron(args.expression)
        next_runs = next_run(fields, count=3)

        print(f"\n{Terminal.colorize('Next 3 runs:', color='cyan')}")
        for run in next_runs:
            print(f"  {run.strftime('%Y-%m-%d %H:%M')} ({run.strftime('%A')})")

        return 0

    except Exception as e:
        print(Terminal.colorize(f"Error: {e}", color="red"))
        return 1


def cmd_next(args: argparse.Namespace) -> int:
    """Show next run times."""
    try:
        fields = parse_cron(args.expression)
        runs = next_run(fields, count=args.count)

        if args.format == "iso":
            for run in runs:
                print(run.isoformat())
        elif args.format == "unix":
            for run in runs:
                print(int(run.timestamp()))
        else:
            for run in runs:
                print(run.strftime("%Y-%m-%d %H:%M"))

        return 0

    except Exception as e:
        print(Terminal.colorize(f"Error: {e}", color="red"))
        return 1


def cmd_validate(args: argparse.Namespace) -> int:
    """Validate cron expression."""
    try:
        parse_cron(args.expression)
        print(Terminal.colorize("✓ Valid cron expression", color="green"))
        return 0
    except Exception as e:
        print(Terminal.colorize(f"✗ Invalid: {e}", color="red"))
        return 1


def cmd_generate(args: argparse.Namespace) -> int:
    """Generate cron expression interactively."""
    print(Terminal.colorize("Cron Expression Generator", color="cyan", bold=True))
    Terminal.print_line("─", width=50)

    fields = []

    prompts = [
        ("Minute (0-59, * for every)", "*"),
        ("Hour (0-23, * for every)", "*"),
        ("Day of month (1-31, * for every)", "*"),
        ("Month (1-12, * for every)", "*"),
        ("Day of week (0-6, 0=Sun, * for every)", "*"),
    ]

    for prompt, default in prompts:
        value = input(f"{prompt} [{default}]: ").strip() or default
        fields.append(value)

    expression = " ".join(fields)

    try:
        parsed = parse_cron(expression)
        runs = next_run(parsed, count=3)

        print(f"\n{Terminal.colorize('Generated expression:', color='green')} {expression}")
        print(f"\n{Terminal.colorize('Next 3 runs:', color='cyan')}")
        for run in runs:
            print(f"  {run.strftime('%Y-%m-%d %H:%M')} ({run.strftime('%A')})")

    except Exception as e:
        print(Terminal.colorize(f"Error: {e}", color="red"))
        return 1

    return 0


def cmd_common(args: argparse.Namespace) -> int:
    """Show common cron expressions."""
    common = [
        ("Every minute", "* * * * *"),
        ("Every 5 minutes", "*/5 * * * *"),
        ("Every 15 minutes", "*/15 * * * *"),
        ("Every hour", "0 * * * *"),
        ("Every 2 hours", "0 */2 * * *"),
        ("Every day at midnight", "0 0 * * *"),
        ("Every day at 6am", "0 6 * * *"),
        ("Every Monday at 9am", "0 9 * * 1"),
        ("Every weekday at 9am", "0 9 * * 1-5"),
        ("First of every month", "0 0 1 * *"),
        ("Every Sunday at 3am", "0 3 * * 0"),
        ("Every 6 hours", "0 */6 * * *"),
        ("Every day at 2:30am", "30 2 * * *"),
        ("Quarterly (Jan, Apr, Jul, Oct)", "0 0 1 1,4,7,10 *"),
    ]

    print(f"\n{Terminal.colorize('Common Cron Expressions', color='cyan', bold=True)}")
    Terminal.print_line("─", width=60)

    for description, expression in common:
        print(f"  {Terminal.colorize(expression, color='yellow'):20} {description}")

    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Cron expression tool - parse, explain, validate, and test cron schedules.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Explain a cron expression
  python cron_tool.py explain "0 9 * * 1-5"
  # Output: Minute: 0, Hour: 9, Day of Month: *, Month: *, Day of Week: 1-5
  #         Next 3 runs: 2024-01-15 09:00 (Monday), ...

  # Explain special expressions
  python cron_tool.py explain @daily
  python cron_tool.py explain @hourly
  python cron_tool.py explain @weekly

  # Show next run times
  python cron_tool.py next "*/15 * * * *"
  # Output: 2024-01-15 10:15, 10:30, 10:45, 11:00, 11:15

  # Show more run times
  python cron_tool.py next "0 9 * * 1" -c 10

  # Output in different formats
  python cron_tool.py next "0 0 * * *" -f iso
  python cron_tool.py next "0 0 * * *" -f unix

  # Validate a cron expression
  python cron_tool.py validate "0 9 * * 1-5"
  # Output: ✓ Valid cron expression

  python cron_tool.py validate "invalid"
  # Output: ✗ Invalid: expected 5 fields

  # Generate expression interactively
  python cron_tool.py generate
  # Prompts for each field (minute, hour, day, month, weekday)

  # Show common cron expressions
  python cron_tool.py common
  # Output: * * * * *      Every minute
  #         0 * * * *      Every hour
  #         0 0 * * *      Every day at midnight
  #         0 9 * * 1-5    Every weekday at 9am
  #         ...

Cron field format:
  ┌───────────── minute (0-59)
  │ ┌───────────── hour (0-23)
  │ │ ┌───────────── day of month (1-31)
  │ │ │ ┌───────────── month (1-12)
  │ │ │ │ ┌───────────── day of week (0-6, 0=Sunday)
  │ │ │ │ │
  * * * * *
""",
    )
    subparsers = parser.add_subparsers(dest="command", help="Command")

    # Explain
    p = subparsers.add_parser("explain", aliases=["e"], help="Explain cron expression")
    p.add_argument("expression", help="Cron expression (5 fields)")
    p.set_defaults(func=cmd_explain)

    # Next
    p = subparsers.add_parser("next", aliases=["n"], help="Show next run times")
    p.add_argument("expression", help="Cron expression")
    p.add_argument("-c", "--count", type=int, default=5, help="Number of runs to show")
    p.add_argument("-f", "--format", choices=["default", "iso", "unix"], default="default")
    p.set_defaults(func=cmd_next)

    # Validate
    p = subparsers.add_parser("validate", aliases=["v"], help="Validate expression")
    p.add_argument("expression", help="Cron expression")
    p.set_defaults(func=cmd_validate)

    # Generate
    p = subparsers.add_parser("generate", aliases=["g"], help="Generate interactively")
    p.set_defaults(func=cmd_generate)

    # Common
    p = subparsers.add_parser("common", aliases=["c"], help="Show common expressions")
    p.set_defaults(func=cmd_common)

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
