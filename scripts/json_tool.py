#!/usr/bin/env python3
"""JSON manipulation tool - pretty print, minify, query, transform."""

import argparse
import json
import sys
from pathlib import Path as PathLib

# Add parent directory to path to import utils
sys.path.insert(0, str(PathLib(__file__).parent.parent))

from utils import JSON, Path, Terminal


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
        print(data)


def cmd_pretty(args: argparse.Namespace) -> int:
    """Pretty print JSON."""
    data = read_input(args.file)
    parsed = json.loads(data)
    result = JSON.pretty(parsed, indent=args.indent)
    write_output(result, args.output)
    return 0


def cmd_minify(args: argparse.Namespace) -> int:
    """Minify JSON."""
    data = read_input(args.file)
    result = JSON.minify(data)
    write_output(result, args.output)
    return 0


def cmd_flatten(args: argparse.Namespace) -> int:
    """Flatten nested JSON."""
    data = read_input(args.file)
    parsed = json.loads(data)
    result = JSON.flatten(parsed, separator=args.sep)
    write_output(json.dumps(result, indent=2), args.output)
    return 0


def cmd_unflatten(args: argparse.Namespace) -> int:
    """Unflatten JSON."""
    data = read_input(args.file)
    parsed = json.loads(data)
    result = JSON.unflatten(parsed, separator=args.sep)
    write_output(json.dumps(result, indent=2), args.output)
    return 0


def cmd_query(args: argparse.Namespace) -> int:
    """Query JSON with dot notation path."""
    data = read_input(args.file)
    parsed = json.loads(data)

    # Navigate using dot notation: "users.0.name"
    path_parts = args.path.split(".")
    result = parsed

    for part in path_parts:
        if isinstance(result, list):
            try:
                result = result[int(part)]
            except (ValueError, IndexError):
                print(Terminal.colorize(f"Invalid index: {part}", color="red"), file=sys.stderr)
                return 1
        elif isinstance(result, dict):
            if part in result:
                result = result[part]
            else:
                print(Terminal.colorize(f"Key not found: {part}", color="red"), file=sys.stderr)
                return 1
        else:
            print(Terminal.colorize(f"Cannot navigate into: {type(result)}", color="red"), file=sys.stderr)
            return 1

    if isinstance(result, (dict, list)):
        write_output(json.dumps(result, indent=2), args.output)
    else:
        write_output(str(result), args.output)
    return 0


def cmd_keys(args: argparse.Namespace) -> int:
    """List all keys in JSON."""
    data = read_input(args.file)
    parsed = json.loads(data)

    def get_keys(obj: dict | list, prefix: str = "") -> list[str]:
        keys = []
        if isinstance(obj, dict):
            for k, v in obj.items():
                full_key = f"{prefix}.{k}" if prefix else k
                keys.append(full_key)
                if isinstance(v, (dict, list)):
                    keys.extend(get_keys(v, full_key))
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                if isinstance(item, (dict, list)):
                    keys.extend(get_keys(item, f"{prefix}.{i}"))
        return keys

    keys = get_keys(parsed)
    write_output("\n".join(keys), args.output)
    return 0


def cmd_validate(args: argparse.Namespace) -> int:
    """Validate JSON syntax."""
    data = read_input(args.file)
    is_valid = JSON.is_valid(data)

    if is_valid:
        print(Terminal.colorize("✓ Valid JSON", color="green"))
        return 0
    else:
        print(Terminal.colorize("✗ Invalid JSON", color="red"))
        return 1


def cmd_diff(args: argparse.Namespace) -> int:
    """Compare two JSON files."""
    data1 = json.loads(Path.read(args.file1))
    data2 = json.loads(Path.read(args.file2))

    def compare(obj1, obj2, path: str = "") -> list[str]:
        diffs = []
        if type(obj1) != type(obj2):
            diffs.append(f"{path}: type mismatch ({type(obj1).__name__} vs {type(obj2).__name__})")
        elif isinstance(obj1, dict):
            all_keys = set(obj1.keys()) | set(obj2.keys())
            for key in sorted(all_keys):
                new_path = f"{path}.{key}" if path else key
                if key not in obj1:
                    diffs.append(Terminal.colorize(f"+ {new_path}", color="green"))
                elif key not in obj2:
                    diffs.append(Terminal.colorize(f"- {new_path}", color="red"))
                else:
                    diffs.extend(compare(obj1[key], obj2[key], new_path))
        elif isinstance(obj1, list):
            if len(obj1) != len(obj2):
                diffs.append(f"{path}: length mismatch ({len(obj1)} vs {len(obj2)})")
            for i in range(min(len(obj1), len(obj2))):
                diffs.extend(compare(obj1[i], obj2[i], f"{path}[{i}]"))
        elif obj1 != obj2:
            diffs.append(f"{path}: {obj1!r} → {obj2!r}")
        return diffs

    differences = compare(data1, data2)
    if differences:
        print("\n".join(differences))
        return 1
    else:
        print(Terminal.colorize("Files are identical", color="green"))
        return 0


def cmd_merge(args: argparse.Namespace) -> int:
    """Merge multiple JSON files."""
    result = {}
    for file_path in args.files:
        data = json.loads(Path.read(file_path))
        if isinstance(data, dict):
            result.update(data)
        else:
            print(
                Terminal.colorize(f"Skipping {file_path}: not an object", color="yellow"),
                file=sys.stderr,
            )

    write_output(json.dumps(result, indent=2), args.output)
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="JSON manipulation tool - pretty print, minify, query, flatten, diff, merge.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Pretty print JSON file
  python json_tool.py pretty data.json
  python json_tool.py pretty data.json --indent 4

  # Pretty print from stdin (pipe from curl, etc.)
  curl -s api.example.com/data | python json_tool.py pretty

  # Minify JSON (remove whitespace)
  python json_tool.py minify data.json -o data.min.json
  # Input:  { "name": "John", "age": 30 }
  # Output: {"name":"John","age":30}

  # Query nested values with dot notation
  python json_tool.py query "users.0.name" data.json
  python json_tool.py query "config.database.host" settings.json
  # Input:  {"users": [{"name": "Alice"}]}
  # Output: Alice

  # List all keys in JSON
  python json_tool.py keys data.json
  # Output:
  #   users
  #   users.0.name
  #   users.0.email

  # Flatten nested JSON to dot notation
  python json_tool.py flatten data.json
  # Input:  {"user": {"name": "John"}}
  # Output: {"user.name": "John"}

  # Unflatten back to nested
  python json_tool.py unflatten flat.json

  # Validate JSON syntax
  python json_tool.py validate data.json
  # Output: ✓ Valid JSON

  # Compare two JSON files
  python json_tool.py diff old.json new.json
  # Output:
  #   + config.newKey
  #   - config.removedKey
  #   ~ config.changedKey: "old" → "new"

  # Merge multiple JSON files
  python json_tool.py merge base.json override.json -o merged.json
""",
    )
    subparsers = parser.add_subparsers(dest="command", help="command to run")

    # Pretty
    p = subparsers.add_parser("pretty", help="Pretty print JSON")
    p.add_argument("file", nargs="?", help="Input file (stdin if omitted)")
    p.add_argument("-o", "--output", help="Output file")
    p.add_argument("--indent", type=int, default=2, help="Indentation (default: 2)")
    p.set_defaults(func=cmd_pretty)

    # Minify
    p = subparsers.add_parser("minify", help="Minify JSON")
    p.add_argument("file", nargs="?", help="Input file (stdin if omitted)")
    p.add_argument("-o", "--output", help="Output file")
    p.set_defaults(func=cmd_minify)

    # Flatten
    p = subparsers.add_parser("flatten", help="Flatten nested JSON")
    p.add_argument("file", nargs="?", help="Input file (stdin if omitted)")
    p.add_argument("-o", "--output", help="Output file")
    p.add_argument("--sep", default=".", help="Key separator (default: .)")
    p.set_defaults(func=cmd_flatten)

    # Unflatten
    p = subparsers.add_parser("unflatten", help="Unflatten JSON")
    p.add_argument("file", nargs="?", help="Input file (stdin if omitted)")
    p.add_argument("-o", "--output", help="Output file")
    p.add_argument("--sep", default=".", help="Key separator (default: .)")
    p.set_defaults(func=cmd_unflatten)

    # Query
    p = subparsers.add_parser("query", aliases=["q"], help="Query JSON with path")
    p.add_argument("path", help="Dot notation path (e.g., users.0.name)")
    p.add_argument("file", nargs="?", help="Input file (stdin if omitted)")
    p.add_argument("-o", "--output", help="Output file")
    p.set_defaults(func=cmd_query)

    # Keys
    p = subparsers.add_parser("keys", help="List all keys")
    p.add_argument("file", nargs="?", help="Input file (stdin if omitted)")
    p.add_argument("-o", "--output", help="Output file")
    p.set_defaults(func=cmd_keys)

    # Validate
    p = subparsers.add_parser("validate", help="Validate JSON syntax")
    p.add_argument("file", nargs="?", help="Input file (stdin if omitted)")
    p.set_defaults(func=cmd_validate)

    # Diff
    p = subparsers.add_parser("diff", help="Compare two JSON files")
    p.add_argument("file1", help="First JSON file")
    p.add_argument("file2", help="Second JSON file")
    p.set_defaults(func=cmd_diff)

    # Merge
    p = subparsers.add_parser("merge", help="Merge JSON files")
    p.add_argument("files", nargs="+", help="JSON files to merge")
    p.add_argument("-o", "--output", help="Output file")
    p.set_defaults(func=cmd_merge)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 0

    try:
        return args.func(args)
    except json.JSONDecodeError as e:
        print(Terminal.colorize(f"JSON parse error: {e}", color="red"), file=sys.stderr)
        return 1
    except FileNotFoundError as e:
        print(Terminal.colorize(f"File not found: {e}", color="red"), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
