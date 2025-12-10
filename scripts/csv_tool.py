#!/usr/bin/env python3
"""CSV operations - filter, sort, convert, stats."""

import argparse
import csv
import io
import json
import sys
from collections import Counter
from pathlib import Path as PathLib

# Add parent directory to path to import utils
sys.path.insert(0, str(PathLib(__file__).parent.parent))

from utils import Path, Terminal


def read_csv(file_path: str | None, delimiter: str = ",") -> tuple[list[str], list[dict]]:
    """Read CSV from file or stdin, return headers and rows."""
    if file_path:
        content = Path.read(file_path)
    else:
        content = sys.stdin.read()

    reader = csv.DictReader(io.StringIO(content), delimiter=delimiter)
    rows = list(reader)
    headers = reader.fieldnames or []
    return headers, rows


def write_csv(
    headers: list[str], rows: list[dict], output: str | None, delimiter: str = ","
) -> None:
    """Write CSV to file or stdout."""
    if output:
        with open(output, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=headers, delimiter=delimiter)
            writer.writeheader()
            writer.writerows(rows)
        print(Terminal.colorize(f"Written to {output}", color="green"), file=sys.stderr)
    else:
        writer = csv.DictWriter(sys.stdout, fieldnames=headers, delimiter=delimiter)
        writer.writeheader()
        writer.writerows(rows)


def cmd_head(args: argparse.Namespace) -> int:
    """Show first N rows."""
    headers, rows = read_csv(args.file, args.delimiter)
    write_csv(headers, rows[: args.n], args.output, args.delimiter)
    return 0


def cmd_tail(args: argparse.Namespace) -> int:
    """Show last N rows."""
    headers, rows = read_csv(args.file, args.delimiter)
    write_csv(headers, rows[-args.n :], args.output, args.delimiter)
    return 0


def cmd_columns(args: argparse.Namespace) -> int:
    """List column names."""
    headers, _ = read_csv(args.file, args.delimiter)
    for i, header in enumerate(headers, 1):
        print(f"{i}. {header}")
    return 0


def cmd_select(args: argparse.Namespace) -> int:
    """Select specific columns."""
    headers, rows = read_csv(args.file, args.delimiter)

    selected = args.cols.split(",")
    for col in selected:
        if col not in headers:
            print(Terminal.colorize(f"Column not found: {col}", color="red"), file=sys.stderr)
            return 1

    new_rows = [{col: row[col] for col in selected} for row in rows]
    write_csv(selected, new_rows, args.output, args.delimiter)
    return 0


def cmd_filter(args: argparse.Namespace) -> int:
    """Filter rows by condition."""
    headers, rows = read_csv(args.file, args.delimiter)

    col, op, value = args.condition.split(":", 2)
    if col not in headers:
        print(Terminal.colorize(f"Column not found: {col}", color="red"), file=sys.stderr)
        return 1

    def match(row: dict) -> bool:
        cell = row.get(col, "")
        if op == "eq":
            return cell == value
        elif op == "ne":
            return cell != value
        elif op == "contains":
            return value in cell
        elif op == "startswith":
            return cell.startswith(value)
        elif op == "endswith":
            return cell.endswith(value)
        elif op == "gt":
            try:
                return float(cell) > float(value)
            except ValueError:
                return False
        elif op == "lt":
            try:
                return float(cell) < float(value)
            except ValueError:
                return False
        elif op == "empty":
            return not cell.strip()
        elif op == "notempty":
            return bool(cell.strip())
        return False

    filtered = [row for row in rows if match(row)]
    print(
        Terminal.colorize(f"Matched {len(filtered)}/{len(rows)} rows", color="cyan"),
        file=sys.stderr,
    )
    write_csv(headers, filtered, args.output, args.delimiter)
    return 0


def cmd_sort(args: argparse.Namespace) -> int:
    """Sort by column."""
    headers, rows = read_csv(args.file, args.delimiter)

    if args.col not in headers:
        print(Terminal.colorize(f"Column not found: {args.col}", color="red"), file=sys.stderr)
        return 1

    def sort_key(row: dict):
        val = row.get(args.col, "")
        if args.numeric:
            try:
                return float(val)
            except ValueError:
                return float("inf")
        return val.lower()

    sorted_rows = sorted(rows, key=sort_key, reverse=args.reverse)
    write_csv(headers, sorted_rows, args.output, args.delimiter)
    return 0


def cmd_unique(args: argparse.Namespace) -> int:
    """Get unique values in a column."""
    headers, rows = read_csv(args.file, args.delimiter)

    if args.col not in headers:
        print(Terminal.colorize(f"Column not found: {args.col}", color="red"), file=sys.stderr)
        return 1

    values = [row.get(args.col, "") for row in rows]
    counter = Counter(values)

    if args.count:
        for value, count in counter.most_common():
            print(f"{count}\t{value}")
    else:
        for value in sorted(set(values)):
            print(value)
    return 0


def cmd_stats(args: argparse.Namespace) -> int:
    """Show statistics for CSV."""
    headers, rows = read_csv(args.file, args.delimiter)

    print(f"\n{Terminal.colorize('CSV Statistics', color='cyan', bold=True)}")
    Terminal.print_line("─", width=40)
    print(f"Rows: {len(rows)}")
    print(f"Columns: {len(headers)}")
    print()

    for header in headers:
        values = [row.get(header, "") for row in rows]
        non_empty = [v for v in values if v.strip()]
        unique = len(set(values))

        print(f"{Terminal.colorize(header, color='cyan', bold=True)}:")
        print(f"  Non-empty: {len(non_empty)}/{len(values)}")
        print(f"  Unique: {unique}")

        # Try numeric stats
        try:
            nums = [float(v) for v in non_empty if v]
            if nums:
                print(f"  Min: {min(nums)}")
                print(f"  Max: {max(nums)}")
                print(f"  Avg: {sum(nums)/len(nums):.2f}")
        except ValueError:
            pass
        print()

    return 0


def cmd_to_json(args: argparse.Namespace) -> int:
    """Convert CSV to JSON."""
    _, rows = read_csv(args.file, args.delimiter)
    output = json.dumps(rows, indent=2)

    if args.output:
        Path.write(args.output, content=output)
        print(Terminal.colorize(f"Written to {args.output}", color="green"), file=sys.stderr)
    else:
        print(output)
    return 0


def cmd_from_json(args: argparse.Namespace) -> int:
    """Convert JSON to CSV."""
    if args.file:
        content = Path.read(args.file)
    else:
        content = sys.stdin.read()

    data = json.loads(content)
    if not isinstance(data, list) or not data:
        print(Terminal.colorize("JSON must be a non-empty array", color="red"), file=sys.stderr)
        return 1

    headers = list(data[0].keys())
    write_csv(headers, data, args.output, args.delimiter)
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="CSV manipulation tool - filter, sort, select columns, convert, stats.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Show first/last N rows
  python csv_tool.py head data.csv
  python csv_tool.py head -n 5 data.csv
  python csv_tool.py tail -n 20 data.csv

  # List column names
  python csv_tool.py columns data.csv
  # Output:
  #   1. name
  #   2. email
  #   3. age

  # Select specific columns
  python csv_tool.py select "name,email" data.csv
  python csv_tool.py select "name,age" data.csv -o subset.csv

  # Filter rows by condition
  python csv_tool.py filter "age:gt:30" data.csv
  python csv_tool.py filter "status:eq:active" data.csv
  python csv_tool.py filter "email:contains:@gmail" data.csv
  python csv_tool.py filter "name:startswith:John" data.csv
  # Operators: eq, ne, contains, startswith, endswith, gt, lt, empty, notempty

  # Sort by column
  python csv_tool.py sort age data.csv --numeric --reverse
  python csv_tool.py sort name data.csv

  # Get unique values in a column
  python csv_tool.py unique status data.csv
  python csv_tool.py unique country data.csv --count
  # Output:
  #   42  USA
  #   31  Canada
  #   15  UK

  # Show statistics for all columns
  python csv_tool.py stats data.csv

  # Convert CSV to JSON
  python csv_tool.py to-json data.csv -o data.json

  # Convert JSON array to CSV
  python csv_tool.py from-json data.json -o data.csv

  # Use different delimiter (e.g., TSV)
  python csv_tool.py -d "\\t" head data.tsv
""",
    )
    parser.add_argument("-d", "--delimiter", default=",", help="field delimiter (default: comma)")
    subparsers = parser.add_subparsers(dest="command", help="command to run")

    # Head
    p = subparsers.add_parser("head", help="Show first N rows")
    p.add_argument("file", nargs="?", help="Input file (stdin if omitted)")
    p.add_argument("-n", type=int, default=10, help="Number of rows (default: 10)")
    p.add_argument("-o", "--output", help="Output file")
    p.set_defaults(func=cmd_head)

    # Tail
    p = subparsers.add_parser("tail", help="Show last N rows")
    p.add_argument("file", nargs="?", help="Input file (stdin if omitted)")
    p.add_argument("-n", type=int, default=10, help="Number of rows (default: 10)")
    p.add_argument("-o", "--output", help="Output file")
    p.set_defaults(func=cmd_tail)

    # Columns
    p = subparsers.add_parser("columns", aliases=["cols"], help="List column names")
    p.add_argument("file", nargs="?", help="Input file (stdin if omitted)")
    p.set_defaults(func=cmd_columns)

    # Select
    p = subparsers.add_parser("select", help="Select specific columns")
    p.add_argument("cols", help="Comma-separated column names")
    p.add_argument("file", nargs="?", help="Input file (stdin if omitted)")
    p.add_argument("-o", "--output", help="Output file")
    p.set_defaults(func=cmd_select)

    # Filter
    p = subparsers.add_parser("filter", help="Filter rows")
    p.add_argument(
        "condition",
        help="Filter: col:op:value (ops: eq,ne,contains,startswith,endswith,gt,lt,empty,notempty)",
    )
    p.add_argument("file", nargs="?", help="Input file (stdin if omitted)")
    p.add_argument("-o", "--output", help="Output file")
    p.set_defaults(func=cmd_filter)

    # Sort
    p = subparsers.add_parser("sort", help="Sort by column")
    p.add_argument("col", help="Column to sort by")
    p.add_argument("file", nargs="?", help="Input file (stdin if omitted)")
    p.add_argument("-r", "--reverse", action="store_true", help="Reverse order")
    p.add_argument("-n", "--numeric", action="store_true", help="Numeric sort")
    p.add_argument("-o", "--output", help="Output file")
    p.set_defaults(func=cmd_sort)

    # Unique
    p = subparsers.add_parser("unique", aliases=["uniq"], help="Unique values in column")
    p.add_argument("col", help="Column name")
    p.add_argument("file", nargs="?", help="Input file (stdin if omitted)")
    p.add_argument("-c", "--count", action="store_true", help="Show counts")
    p.set_defaults(func=cmd_unique)

    # Stats
    p = subparsers.add_parser("stats", help="Show statistics")
    p.add_argument("file", nargs="?", help="Input file (stdin if omitted)")
    p.set_defaults(func=cmd_stats)

    # To JSON
    p = subparsers.add_parser("to-json", help="Convert to JSON")
    p.add_argument("file", nargs="?", help="Input file (stdin if omitted)")
    p.add_argument("-o", "--output", help="Output file")
    p.set_defaults(func=cmd_to_json)

    # From JSON
    p = subparsers.add_parser("from-json", help="Convert from JSON")
    p.add_argument("file", nargs="?", help="Input file (stdin if omitted)")
    p.add_argument("-o", "--output", help="Output file")
    p.set_defaults(func=cmd_from_json)

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
