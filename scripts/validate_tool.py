#!/usr/bin/env python3
"""Validate data formats - emails, URLs, phones, IPs, JSON schemas."""

import argparse
import json
import re
import sys
from pathlib import Path as PathLib

# Add parent directory to path to import utils
sys.path.insert(0, str(PathLib(__file__).parent.parent))

from utils import Path, Terminal, Validator


def read_input(file_path: str | None, text: str | None = None) -> str:
    """Read input from text arg, file, or stdin."""
    if text:
        return text
    if file_path:
        return Path.read(file_path)
    return sys.stdin.read().strip()


def validate_items(
    items: list[str],
    validator_func,
    item_type: str,
    verbose: bool = False,
) -> int:
    """Validate a list of items."""
    valid_count = 0
    invalid_count = 0

    for item in items:
        item = item.strip()
        if not item:
            continue

        is_valid = validator_func(item)

        if verbose:
            if is_valid:
                print(Terminal.colorize(f"✓ {item}", color="green"))
            else:
                print(Terminal.colorize(f"✗ {item}", color="red"))

        if is_valid:
            valid_count += 1
        else:
            invalid_count += 1

    if not verbose:
        if invalid_count == 0:
            print(Terminal.colorize(f"All {valid_count} {item_type}(s) valid", color="green"))
        else:
            print(Terminal.colorize(
                f"Valid: {valid_count}, Invalid: {invalid_count}",
                color="yellow" if valid_count > 0 else "red"
            ))

    return 0 if invalid_count == 0 else 1


def cmd_email(args: argparse.Namespace) -> int:
    """Validate email addresses."""
    text = read_input(args.file, args.value)
    items = text.splitlines() if "\n" in text else [text]
    return validate_items(items, Validator.email, "email", args.verbose)


def cmd_url(args: argparse.Namespace) -> int:
    """Validate URLs."""
    text = read_input(args.file, args.value)
    items = text.splitlines() if "\n" in text else [text]
    return validate_items(items, Validator.url, "URL", args.verbose)


def cmd_phone(args: argparse.Namespace) -> int:
    """Validate phone numbers."""
    text = read_input(args.file, args.value)
    items = text.splitlines() if "\n" in text else [text]
    return validate_items(items, Validator.phone, "phone", args.verbose)


def cmd_ip(args: argparse.Namespace) -> int:
    """Validate IP addresses."""
    import ipaddress

    def is_valid_ip(value: str) -> bool:
        try:
            ip = ipaddress.ip_address(value)
            if args.v4 and ip.version != 4:
                return False
            if args.v6 and ip.version != 6:
                return False
            return True
        except ValueError:
            return False

    text = read_input(args.file, args.value)
    items = text.splitlines() if "\n" in text else [text]
    return validate_items(items, is_valid_ip, "IP", args.verbose)


def cmd_uuid(args: argparse.Namespace) -> int:
    """Validate UUIDs."""
    text = read_input(args.file, args.value)
    items = text.splitlines() if "\n" in text else [text]
    return validate_items(items, Validator.uuid, "UUID", args.verbose)


def cmd_credit_card(args: argparse.Namespace) -> int:
    """Validate credit card numbers."""
    text = read_input(args.file, args.value)
    items = text.splitlines() if "\n" in text else [text]
    return validate_items(items, Validator.credit_card, "credit card", args.verbose)


def cmd_json(args: argparse.Namespace) -> int:
    """Validate JSON syntax."""
    text = read_input(args.file, args.value)

    try:
        data = json.loads(text)

        if args.schema:
            # Validate against JSON schema
            try:
                import jsonschema
                schema = json.loads(Path.read(args.schema))
                jsonschema.validate(data, schema)
                print(Terminal.colorize("✓ Valid JSON, matches schema", color="green"))
            except ImportError:
                print(Terminal.colorize("jsonschema not installed", color="yellow"))
                print(Terminal.colorize("✓ Valid JSON (schema not checked)", color="green"))
            except jsonschema.ValidationError as e:
                print(Terminal.colorize(f"✗ Schema validation failed: {e.message}", color="red"))
                return 1
        else:
            print(Terminal.colorize("✓ Valid JSON", color="green"))

        if args.stats:
            print(f"\nType: {type(data).__name__}")
            if isinstance(data, list):
                print(f"Items: {len(data)}")
            elif isinstance(data, dict):
                print(f"Keys: {len(data)}")
                print(f"Top-level keys: {', '.join(list(data.keys())[:10])}")

        return 0

    except json.JSONDecodeError as e:
        print(Terminal.colorize(f"✗ Invalid JSON: {e}", color="red"))
        return 1


def cmd_regex(args: argparse.Namespace) -> int:
    """Validate against regex pattern."""
    text = read_input(args.file, args.value)
    items = text.splitlines() if "\n" in text else [text]

    try:
        flags = re.IGNORECASE if args.ignore_case else 0
        pattern = re.compile(args.pattern, flags)
    except re.error as e:
        print(Terminal.colorize(f"Invalid regex: {e}", color="red"))
        return 1

    def matches_pattern(value: str) -> bool:
        return bool(pattern.fullmatch(value) if args.full else pattern.search(value))

    return validate_items(items, matches_pattern, "item", args.verbose)


def cmd_file(args: argparse.Namespace) -> int:
    """Validate file properties."""
    path = PathLib(args.path)

    checks = []

    # Existence
    if path.exists():
        checks.append((True, "exists"))
    else:
        checks.append((False, "exists"))
        print(Terminal.colorize(f"✗ File does not exist: {args.path}", color="red"))
        return 1

    # Type
    if args.is_file and not path.is_file():
        checks.append((False, "is file"))
    elif args.is_dir and not path.is_dir():
        checks.append((False, "is directory"))
    else:
        if path.is_file():
            checks.append((True, "is file"))
        else:
            checks.append((True, "is directory"))

    # Size
    if args.min_size and path.is_file():
        size = path.stat().st_size
        if size < args.min_size:
            checks.append((False, f"min size {args.min_size}"))
        else:
            checks.append((True, f"size >= {args.min_size}"))

    if args.max_size and path.is_file():
        size = path.stat().st_size
        if size > args.max_size:
            checks.append((False, f"max size {args.max_size}"))
        else:
            checks.append((True, f"size <= {args.max_size}"))

    # Extension
    if args.extension:
        if path.suffix.lower() == f".{args.extension.lower().lstrip('.')}":
            checks.append((True, f"extension .{args.extension}"))
        else:
            checks.append((False, f"extension .{args.extension}"))

    # Print results
    all_passed = True
    for passed, desc in checks:
        if passed:
            print(Terminal.colorize(f"✓ {desc}", color="green"))
        else:
            print(Terminal.colorize(f"✗ {desc}", color="red"))
            all_passed = False

    return 0 if all_passed else 1


def cmd_all(args: argparse.Namespace) -> int:
    """Auto-detect and validate."""
    text = read_input(args.file, args.value)
    items = text.splitlines() if "\n" in text else [text]

    validators = [
        ("email", Validator.email),
        ("URL", Validator.url),
        ("UUID", Validator.uuid),
        ("phone", Validator.phone),
        ("credit card", Validator.credit_card),
    ]

    for item in items:
        item = item.strip()
        if not item:
            continue

        detected = []
        for name, func in validators:
            if func(item):
                detected.append(name)

        if detected:
            print(f"{item}: {Terminal.colorize(', '.join(detected), color='green')}")
        else:
            print(f"{item}: {Terminal.colorize('unknown format', color='yellow')}")

    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validation tool - validate emails, URLs, IPs, JSON, and more.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Validate email addresses
  python validate_tool.py email "user@example.com"
  # Output: All 1 email(s) valid

  # Validate multiple emails from file
  python validate_tool.py email -f emails.txt -v
  # Output: ✓ user@example.com
  #         ✗ invalid-email
  #         ✓ another@test.com

  # Validate URLs
  python validate_tool.py url "https://example.com"
  python validate_tool.py url -f urls.txt

  # Validate phone numbers
  python validate_tool.py phone "+1-555-123-4567"
  python validate_tool.py phone -f phones.txt -v

  # Validate IP addresses
  python validate_tool.py ip "192.168.1.1"
  python validate_tool.py ip "2001:db8::1"      # IPv6
  python validate_tool.py ip "192.168.1.1" -4   # IPv4 only
  python validate_tool.py ip "::1" -6           # IPv6 only

  # Validate UUIDs
  python validate_tool.py uuid "550e8400-e29b-41d4-a716-446655440000"

  # Validate credit card numbers (Luhn algorithm)
  python validate_tool.py cc "4111111111111111"

  # Validate JSON syntax
  python validate_tool.py json '{"key": "value"}'
  python validate_tool.py json -f data.json
  python validate_tool.py json -f data.json --stats   # show type and key count

  # Validate JSON against schema
  python validate_tool.py json -f data.json -s schema.json

  # Validate against custom regex
  python validate_tool.py regex "^[A-Z]{2}\\d{4}$" "AB1234"
  python validate_tool.py regex "^\\d{5}$" -f zipcodes.txt --full

  # Validate file properties
  python validate_tool.py file myfile.txt
  python validate_tool.py file myfile.txt --is-file
  python validate_tool.py file mydir/ --is-dir
  python validate_tool.py file data.json --extension json
  python validate_tool.py file upload.zip --min-size 1024 --max-size 10485760

  # Auto-detect format
  python validate_tool.py all "user@example.com"
  # Output: user@example.com: email

  python validate_tool.py all -f mixed_data.txt
""",
    )
    subparsers = parser.add_subparsers(dest="command", help="Command")

    # Email
    p = subparsers.add_parser("email", help="Validate emails")
    p.add_argument("value", nargs="?", help="Email(s) to validate")
    p.add_argument("-f", "--file", help="Read from file")
    p.add_argument("-v", "--verbose", action="store_true", help="Show each result")
    p.set_defaults(func=cmd_email)

    # URL
    p = subparsers.add_parser("url", help="Validate URLs")
    p.add_argument("value", nargs="?", help="URL(s) to validate")
    p.add_argument("-f", "--file", help="Read from file")
    p.add_argument("-v", "--verbose", action="store_true", help="Show each result")
    p.set_defaults(func=cmd_url)

    # Phone
    p = subparsers.add_parser("phone", help="Validate phones")
    p.add_argument("value", nargs="?", help="Phone(s) to validate")
    p.add_argument("-f", "--file", help="Read from file")
    p.add_argument("-v", "--verbose", action="store_true", help="Show each result")
    p.set_defaults(func=cmd_phone)

    # IP
    p = subparsers.add_parser("ip", help="Validate IPs")
    p.add_argument("value", nargs="?", help="IP(s) to validate")
    p.add_argument("-f", "--file", help="Read from file")
    p.add_argument("-4", "--v4", action="store_true", help="IPv4 only")
    p.add_argument("-6", "--v6", action="store_true", help="IPv6 only")
    p.add_argument("-v", "--verbose", action="store_true", help="Show each result")
    p.set_defaults(func=cmd_ip)

    # UUID
    p = subparsers.add_parser("uuid", help="Validate UUIDs")
    p.add_argument("value", nargs="?", help="UUID(s) to validate")
    p.add_argument("-f", "--file", help="Read from file")
    p.add_argument("-v", "--verbose", action="store_true", help="Show each result")
    p.set_defaults(func=cmd_uuid)

    # Credit card
    p = subparsers.add_parser("cc", aliases=["creditcard"], help="Validate credit cards")
    p.add_argument("value", nargs="?", help="Card number(s)")
    p.add_argument("-f", "--file", help="Read from file")
    p.add_argument("-v", "--verbose", action="store_true", help="Show each result")
    p.set_defaults(func=cmd_credit_card)

    # JSON
    p = subparsers.add_parser("json", help="Validate JSON")
    p.add_argument("value", nargs="?", help="JSON string")
    p.add_argument("-f", "--file", help="JSON file")
    p.add_argument("-s", "--schema", help="JSON schema file")
    p.add_argument("--stats", action="store_true", help="Show stats")
    p.set_defaults(func=cmd_json)

    # Regex
    p = subparsers.add_parser("regex", help="Validate against regex")
    p.add_argument("pattern", help="Regex pattern")
    p.add_argument("value", nargs="?", help="Value(s) to test")
    p.add_argument("-f", "--file", help="Read from file")
    p.add_argument("-i", "--ignore-case", action="store_true")
    p.add_argument("--full", action="store_true", help="Full match required")
    p.add_argument("-v", "--verbose", action="store_true", help="Show each result")
    p.set_defaults(func=cmd_regex)

    # File
    p = subparsers.add_parser("file", help="Validate file properties")
    p.add_argument("path", help="File path")
    p.add_argument("--is-file", action="store_true", help="Must be a file")
    p.add_argument("--is-dir", action="store_true", help="Must be a directory")
    p.add_argument("--min-size", type=int, help="Minimum size in bytes")
    p.add_argument("--max-size", type=int, help="Maximum size in bytes")
    p.add_argument("--extension", help="Required extension")
    p.set_defaults(func=cmd_file)

    # All (auto-detect)
    p = subparsers.add_parser("all", aliases=["auto"], help="Auto-detect format")
    p.add_argument("value", nargs="?", help="Value(s) to check")
    p.add_argument("-f", "--file", help="Read from file")
    p.set_defaults(func=cmd_all)

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
