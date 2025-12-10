#!/usr/bin/env python3
"""SQLite utilities - query, dump, import CSV."""

import argparse
import csv
import json
import sqlite3
import sys
from pathlib import Path as PathLib

# Add parent directory to path to import utils
sys.path.insert(0, str(PathLib(__file__).parent.parent))

from utils import Path, Terminal


def format_value(value) -> str:
    """Format value for display."""
    if value is None:
        return Terminal.colorize("NULL", color="yellow")
    if isinstance(value, bytes):
        return f"<{len(value)} bytes>"
    return str(value)


def print_table(headers: list[str], rows: list, max_width: int = 50) -> None:
    """Print data as formatted table."""
    if not rows:
        print(Terminal.colorize("No results", color="yellow"))
        return

    # Calculate column widths
    widths = [len(str(h)) for h in headers]
    for row in rows:
        for i, val in enumerate(row):
            val_str = format_value(val)
            widths[i] = min(max_width, max(widths[i], len(val_str)))

    # Print header
    header_line = " | ".join(str(h).ljust(widths[i]) for i, h in enumerate(headers))
    print(Terminal.colorize(header_line, color="cyan", bold=True))
    print("-+-".join("-" * w for w in widths))

    # Print rows
    for row in rows:
        row_line = " | ".join(
            format_value(val)[:widths[i]].ljust(widths[i])
            for i, val in enumerate(row)
        )
        print(row_line)


def cmd_query(args: argparse.Namespace) -> int:
    """Execute SQL query."""
    try:
        conn = sqlite3.connect(args.database)
        cursor = conn.cursor()

        cursor.execute(args.sql)

        if cursor.description:
            headers = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()

            if args.format == "table":
                print_table(headers, rows)
            elif args.format == "csv":
                writer = csv.writer(sys.stdout)
                writer.writerow(headers)
                writer.writerows(rows)
            elif args.format == "json":
                result = [dict(zip(headers, row)) for row in rows]
                print(json.dumps(result, indent=2, default=str))
            elif args.format == "line":
                for row in rows:
                    for i, header in enumerate(headers):
                        print(f"{Terminal.colorize(header, color='cyan')}: {format_value(row[i])}")
                    print()

            if args.format == "table":
                print(f"\n{len(rows)} row(s)")
        else:
            print(f"Rows affected: {cursor.rowcount}")
            conn.commit()

        conn.close()
        return 0

    except sqlite3.Error as e:
        print(Terminal.colorize(f"SQL Error: {e}", color="red"))
        return 1


def cmd_tables(args: argparse.Namespace) -> int:
    """List all tables."""
    try:
        conn = sqlite3.connect(args.database)
        cursor = conn.cursor()

        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tables = cursor.fetchall()

        print(f"\n{Terminal.colorize('Tables', color='cyan', bold=True)}")
        Terminal.print_line("─", width=40)

        for (table,) in tables:
            cursor.execute(f"SELECT COUNT(*) FROM '{table}'")
            count = cursor.fetchone()[0]
            print(f"  {table:<30} {count:>8} rows")

        conn.close()
        return 0

    except sqlite3.Error as e:
        print(Terminal.colorize(f"Error: {e}", color="red"))
        return 1


def cmd_schema(args: argparse.Namespace) -> int:
    """Show table schema."""
    try:
        conn = sqlite3.connect(args.database)
        cursor = conn.cursor()

        if args.table:
            cursor.execute(
                "SELECT sql FROM sqlite_master WHERE type='table' AND name=?",
                (args.table,)
            )
            result = cursor.fetchone()
            if result:
                print(result[0])
            else:
                print(Terminal.colorize(f"Table not found: {args.table}", color="red"))
                return 1
        else:
            cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' ORDER BY name")
            for (sql,) in cursor.fetchall():
                if sql:
                    print(sql)
                    print()

        conn.close()
        return 0

    except sqlite3.Error as e:
        print(Terminal.colorize(f"Error: {e}", color="red"))
        return 1


def cmd_describe(args: argparse.Namespace) -> int:
    """Describe table columns."""
    try:
        conn = sqlite3.connect(args.database)
        cursor = conn.cursor()

        cursor.execute(f"PRAGMA table_info('{args.table}')")
        columns = cursor.fetchall()

        if not columns:
            print(Terminal.colorize(f"Table not found: {args.table}", color="red"))
            return 1

        print(f"\n{Terminal.colorize(f'Table: {args.table}', color='cyan', bold=True)}")
        Terminal.print_line("─", width=60)

        headers = ["#", "Column", "Type", "Nullable", "Default", "PK"]
        rows = [
            (col[0], col[1], col[2], "NO" if col[3] else "YES", col[4], "YES" if col[5] else "")
            for col in columns
        ]
        print_table(headers, rows)

        conn.close()
        return 0

    except sqlite3.Error as e:
        print(Terminal.colorize(f"Error: {e}", color="red"))
        return 1


def cmd_dump(args: argparse.Namespace) -> int:
    """Dump database or table."""
    try:
        conn = sqlite3.connect(args.database)

        if args.table:
            # Dump single table
            cursor = conn.cursor()
            cursor.execute(f"SELECT * FROM '{args.table}'")
            rows = cursor.fetchall()
            headers = [desc[0] for desc in cursor.description]

            if args.format == "csv":
                writer = csv.writer(sys.stdout)
                writer.writerow(headers)
                writer.writerows(rows)
            elif args.format == "json":
                result = [dict(zip(headers, row)) for row in rows]
                print(json.dumps(result, indent=2, default=str))
            else:  # sql
                for row in rows:
                    values = ", ".join(
                        f"'{v}'" if isinstance(v, str) else "NULL" if v is None else str(v)
                        for v in row
                    )
                    print(f"INSERT INTO {args.table} VALUES ({values});")
        else:
            # Dump entire database
            for line in conn.iterdump():
                print(line)

        conn.close()
        return 0

    except sqlite3.Error as e:
        print(Terminal.colorize(f"Error: {e}", color="red"))
        return 1


def cmd_import_csv(args: argparse.Namespace) -> int:
    """Import CSV into table."""
    try:
        conn = sqlite3.connect(args.database)
        cursor = conn.cursor()

        # Read CSV
        with open(args.csv_file, "r") as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        if not rows:
            print(Terminal.colorize("CSV is empty", color="yellow"))
            return 0

        headers = list(rows[0].keys())
        table = args.table or PathLib(args.csv_file).stem

        # Create table if needed
        if args.create:
            columns = ", ".join(f'"{h}" TEXT' for h in headers)
            cursor.execute(f"CREATE TABLE IF NOT EXISTS '{table}' ({columns})")

        # Insert rows
        placeholders = ", ".join("?" for _ in headers)
        sql = f"INSERT INTO '{table}' ({', '.join(f'\"{h}\"' for h in headers)}) VALUES ({placeholders})"

        for row in rows:
            values = [row.get(h) for h in headers]
            cursor.execute(sql, values)

        conn.commit()
        print(Terminal.colorize(f"Imported {len(rows)} rows into {table}", color="green"))

        conn.close()
        return 0

    except (sqlite3.Error, FileNotFoundError) as e:
        print(Terminal.colorize(f"Error: {e}", color="red"))
        return 1


def cmd_vacuum(args: argparse.Namespace) -> int:
    """Optimize database."""
    try:
        import os
        before = os.path.getsize(args.database)

        conn = sqlite3.connect(args.database)
        conn.execute("VACUUM")
        conn.close()

        after = os.path.getsize(args.database)
        saved = before - after

        print(f"Before: {before:,} bytes")
        print(f"After:  {after:,} bytes")
        print(Terminal.colorize(f"Saved:  {saved:,} bytes", color="green"))

        return 0

    except sqlite3.Error as e:
        print(Terminal.colorize(f"Error: {e}", color="red"))
        return 1


def cmd_interactive(args: argparse.Namespace) -> int:
    """Interactive SQL shell."""
    try:
        conn = sqlite3.connect(args.database)
        cursor = conn.cursor()

        print(Terminal.colorize(f"SQLite shell: {args.database}", color="cyan", bold=True))
        print("Type 'quit' or Ctrl+C to exit, '.tables' to list tables")
        Terminal.print_line("─", width=60)

        while True:
            try:
                sql = input(Terminal.colorize("sql> ", color="cyan"))

                if sql.lower() in ("quit", "exit", "q"):
                    break

                if sql == ".tables":
                    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                    for (table,) in cursor.fetchall():
                        print(f"  {table}")
                    continue

                if sql.startswith(".schema"):
                    parts = sql.split()
                    if len(parts) > 1:
                        cursor.execute(
                            "SELECT sql FROM sqlite_master WHERE name=?",
                            (parts[1],)
                        )
                        result = cursor.fetchone()
                        if result:
                            print(result[0])
                    continue

                cursor.execute(sql)

                if cursor.description:
                    headers = [desc[0] for desc in cursor.description]
                    rows = cursor.fetchall()
                    print_table(headers, rows)
                    print(f"\n{len(rows)} row(s)")
                else:
                    conn.commit()
                    print(f"Rows affected: {cursor.rowcount}")

            except sqlite3.Error as e:
                print(Terminal.colorize(f"Error: {e}", color="red"))
            except (KeyboardInterrupt, EOFError):
                break

        conn.close()
        print("\nGoodbye!")
        return 0

    except sqlite3.Error as e:
        print(Terminal.colorize(f"Error: {e}", color="red"))
        return 1


def main() -> int:
    parser = argparse.ArgumentParser(
        description="SQLite tool - query, dump, import, and manage SQLite databases.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Execute SQL query
  python db_tool.py mydb.db query "SELECT * FROM users"
  # Output: Formatted table with results

  # Query with different output formats
  python db_tool.py mydb.db query "SELECT * FROM users" -f csv
  python db_tool.py mydb.db query "SELECT * FROM users" -f json
  python db_tool.py mydb.db query "SELECT * FROM users" -f line

  # List all tables with row counts
  python db_tool.py mydb.db tables
  # Output: users          1234 rows
  #         orders         5678 rows

  # Show table schema
  python db_tool.py mydb.db schema
  python db_tool.py mydb.db schema users

  # Describe table columns
  python db_tool.py mydb.db describe users
  # Output: #  Column  Type     Nullable  Default  PK
  #         0  id      INTEGER  NO        None     YES
  #         1  name    TEXT     YES       None

  # Dump database or table
  python db_tool.py mydb.db dump                    # entire database as SQL
  python db_tool.py mydb.db dump users              # single table
  python db_tool.py mydb.db dump users -f csv       # as CSV
  python db_tool.py mydb.db dump users -f json      # as JSON

  # Import CSV into table
  python db_tool.py mydb.db import data.csv -t users
  python db_tool.py mydb.db import data.csv -c      # create table if needed

  # Optimize database (reclaim space)
  python db_tool.py mydb.db vacuum
  # Output: Before: 1,234,567 bytes, After: 1,000,000 bytes, Saved: 234,567

  # Interactive SQL shell
  python db_tool.py mydb.db shell
  # sql> SELECT * FROM users LIMIT 5;
  # sql> .tables
  # sql> .schema users
  # sql> quit

  # Run without subcommand for interactive shell
  python db_tool.py mydb.db
""",
    )
    parser.add_argument("database", help="Database file")
    subparsers = parser.add_subparsers(dest="command", help="Command")

    # Query
    p = subparsers.add_parser("query", aliases=["q"], help="Execute SQL")
    p.add_argument("sql", help="SQL query")
    p.add_argument("-f", "--format", choices=["table", "csv", "json", "line"], default="table")
    p.set_defaults(func=cmd_query)

    # Tables
    p = subparsers.add_parser("tables", aliases=["t"], help="List tables")
    p.set_defaults(func=cmd_tables)

    # Schema
    p = subparsers.add_parser("schema", help="Show schema")
    p.add_argument("table", nargs="?", help="Table name")
    p.set_defaults(func=cmd_schema)

    # Describe
    p = subparsers.add_parser("describe", aliases=["desc"], help="Describe table")
    p.add_argument("table", help="Table name")
    p.set_defaults(func=cmd_describe)

    # Dump
    p = subparsers.add_parser("dump", help="Dump database/table")
    p.add_argument("table", nargs="?", help="Table to dump")
    p.add_argument("-f", "--format", choices=["sql", "csv", "json"], default="sql")
    p.set_defaults(func=cmd_dump)

    # Import CSV
    p = subparsers.add_parser("import", help="Import CSV")
    p.add_argument("csv_file", help="CSV file to import")
    p.add_argument("-t", "--table", help="Target table (default: filename)")
    p.add_argument("-c", "--create", action="store_true", help="Create table if needed")
    p.set_defaults(func=cmd_import_csv)

    # Vacuum
    p = subparsers.add_parser("vacuum", help="Optimize database")
    p.set_defaults(func=cmd_vacuum)

    # Interactive
    p = subparsers.add_parser("shell", aliases=["i"], help="Interactive shell")
    p.set_defaults(func=cmd_interactive)

    args = parser.parse_args()

    if not args.command:
        # Default to interactive shell
        args.func = cmd_interactive
        return args.func(args)

    try:
        return args.func(args)
    except Exception as e:
        print(Terminal.colorize(f"Error: {e}", color="red"), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
