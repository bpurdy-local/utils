#!/usr/bin/env python3
"""Manage .env files - get, set, list, export, import."""

import argparse
import os
import re
import sys
from pathlib import Path as PathLib

# Add parent directory to path to import utils
sys.path.insert(0, str(PathLib(__file__).parent.parent))

from utils import Env, Path, Terminal


def parse_env_file(file_path: str) -> dict[str, str]:
    """Parse .env file into dict."""
    result = {}
    if not PathLib(file_path).exists():
        return result

    content = Path.read(file_path)
    for line in content.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue

        if "=" in line:
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip()

            # Remove quotes
            if (value.startswith('"') and value.endswith('"')) or \
               (value.startswith("'") and value.endswith("'")):
                value = value[1:-1]

            result[key] = value

    return result


def write_env_file(file_path: str, env_vars: dict[str, str]) -> None:
    """Write dict to .env file."""
    lines = []
    for key, value in sorted(env_vars.items()):
        # Quote if contains spaces or special chars
        if " " in value or "=" in value or '"' in value:
            value = f'"{value}"'
        lines.append(f"{key}={value}")

    Path.write(file_path, content="\n".join(lines) + "\n")


def cmd_get(args: argparse.Namespace) -> int:
    """Get value of env variable."""
    env_vars = parse_env_file(args.file)

    if args.key in env_vars:
        print(env_vars[args.key])
        return 0
    elif args.key in os.environ:
        print(os.environ[args.key])
        return 0
    else:
        if args.default is not None:
            print(args.default)
            return 0
        print(Terminal.colorize(f"Variable not found: {args.key}", color="red"), file=sys.stderr)
        return 1


def cmd_set(args: argparse.Namespace) -> int:
    """Set env variable."""
    env_vars = parse_env_file(args.file)
    env_vars[args.key] = args.value
    write_env_file(args.file, env_vars)
    print(Terminal.colorize(f"Set {args.key}={args.value}", color="green"))
    return 0


def cmd_unset(args: argparse.Namespace) -> int:
    """Remove env variable."""
    env_vars = parse_env_file(args.file)

    if args.key in env_vars:
        del env_vars[args.key]
        write_env_file(args.file, env_vars)
        print(Terminal.colorize(f"Removed {args.key}", color="green"))
        return 0
    else:
        print(Terminal.colorize(f"Variable not found: {args.key}", color="yellow"))
        return 1


def cmd_list(args: argparse.Namespace) -> int:
    """List all env variables."""
    env_vars = parse_env_file(args.file)

    if not env_vars:
        print(Terminal.colorize("No variables found", color="yellow"))
        return 0

    max_key_len = max(len(k) for k in env_vars.keys())

    for key, value in sorted(env_vars.items()):
        if args.values:
            if args.mask and any(s in key.lower() for s in ["secret", "password", "key", "token"]):
                value = "****"
            print(f"{Terminal.colorize(key.ljust(max_key_len), color='cyan')} = {value}")
        else:
            print(key)

    return 0


def cmd_export(args: argparse.Namespace) -> int:
    """Export env vars as shell commands."""
    env_vars = parse_env_file(args.file)

    for key, value in sorted(env_vars.items()):
        # Escape for shell
        value = value.replace("'", "'\"'\"'")
        print(f"export {key}='{value}'")

    return 0


def cmd_diff(args: argparse.Namespace) -> int:
    """Compare two .env files."""
    env1 = parse_env_file(args.file1)
    env2 = parse_env_file(args.file2)

    all_keys = set(env1.keys()) | set(env2.keys())

    has_diff = False
    for key in sorted(all_keys):
        in_1 = key in env1
        in_2 = key in env2

        if in_1 and not in_2:
            has_diff = True
            print(Terminal.colorize(f"- {key}={env1[key]}", color="red"))
        elif in_2 and not in_1:
            has_diff = True
            print(Terminal.colorize(f"+ {key}={env2[key]}", color="green"))
        elif env1[key] != env2[key]:
            has_diff = True
            print(Terminal.colorize(f"~ {key}: {env1[key]} → {env2[key]}", color="yellow"))

    if not has_diff:
        print(Terminal.colorize("Files are identical", color="green"))

    return 0 if not has_diff else 1


def cmd_merge(args: argparse.Namespace) -> int:
    """Merge .env files."""
    result = {}

    for file_path in args.files:
        env_vars = parse_env_file(file_path)
        result.update(env_vars)

    if args.output:
        write_env_file(args.output, result)
        print(Terminal.colorize(f"Merged to {args.output}", color="green"))
    else:
        for key, value in sorted(result.items()):
            print(f"{key}={value}")

    return 0


def cmd_template(args: argparse.Namespace) -> int:
    """Create .env from template."""
    if not PathLib(args.template).exists():
        print(Terminal.colorize(f"Template not found: {args.template}", color="red"))
        return 1

    content = Path.read(args.template)
    env_vars = {}

    for line in content.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue

        if "=" in line:
            key, default = line.split("=", 1)
            key = key.strip()
            default = default.strip().strip('"\'')

            # Check if already set
            current = Env.get(key)
            if current:
                env_vars[key] = current
            elif args.interactive:
                value = Terminal.prompt(f"{key}", default=default or None)
                env_vars[key] = value or default
            else:
                env_vars[key] = default

    write_env_file(args.output, env_vars)
    print(Terminal.colorize(f"Created {args.output}", color="green"))
    return 0


def cmd_validate(args: argparse.Namespace) -> int:
    """Validate .env file has required variables."""
    env_vars = parse_env_file(args.file)

    missing = []
    for key in args.required:
        if key not in env_vars or not env_vars[key]:
            missing.append(key)

    if missing:
        print(Terminal.colorize("Missing required variables:", color="red"))
        for key in missing:
            print(f"  - {key}")
        return 1
    else:
        print(Terminal.colorize("All required variables present", color="green"))
        return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Manage .env files - get, set, list, diff, merge, validate.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Get a variable value
  python env_tool.py get DATABASE_URL
  # Output: postgres://localhost/mydb

  # Get with default value
  python env_tool.py get API_KEY -d "not-set"

  # Set a variable
  python env_tool.py set API_KEY "sk-12345"
  # Output: Set API_KEY=sk-12345

  # Remove a variable
  python env_tool.py unset OLD_VAR

  # List all variables
  python env_tool.py list
  # Output: API_KEY, DATABASE_URL, SECRET_KEY, ...

  # List with values
  python env_tool.py list -v
  # Output: API_KEY = sk-12345

  # List with masked secrets
  python env_tool.py list -v -m
  # Output: API_KEY = ****, DATABASE_URL = postgres://...

  # Export as shell commands
  python env_tool.py export
  # Output: export API_KEY='sk-12345'
  #         export DATABASE_URL='postgres://...'

  # Compare two .env files
  python env_tool.py diff .env.production .env.staging
  # Output: - ONLY_IN_PROD=value
  #         + ONLY_IN_STAGING=value
  #         ~ DIFFERENT=old_val → new_val

  # Merge multiple .env files
  python env_tool.py merge .env.defaults .env.local -o .env
  # Later files override earlier ones

  # Create .env from template
  python env_tool.py template .env.example -o .env
  python env_tool.py template .env.example -o .env -i  # interactive mode

  # Validate required variables exist
  python env_tool.py validate DATABASE_URL API_KEY SECRET_KEY
  # Exit code 0 if all present, 1 if missing

  # Use custom .env file
  python env_tool.py -f .env.production get API_URL
""",
    )
    parser.add_argument("-f", "--file", default=".env", help="Env file (default: .env)")
    subparsers = parser.add_subparsers(dest="command", help="Command")

    # Get
    p = subparsers.add_parser("get", help="Get variable value")
    p.add_argument("key", help="Variable name")
    p.add_argument("-d", "--default", help="Default if not found")
    p.set_defaults(func=cmd_get)

    # Set
    p = subparsers.add_parser("set", help="Set variable")
    p.add_argument("key", help="Variable name")
    p.add_argument("value", help="Variable value")
    p.set_defaults(func=cmd_set)

    # Unset
    p = subparsers.add_parser("unset", aliases=["rm"], help="Remove variable")
    p.add_argument("key", help="Variable name")
    p.set_defaults(func=cmd_unset)

    # List
    p = subparsers.add_parser("list", aliases=["ls"], help="List variables")
    p.add_argument("-v", "--values", action="store_true", help="Show values")
    p.add_argument("-m", "--mask", action="store_true", help="Mask secrets")
    p.set_defaults(func=cmd_list)

    # Export
    p = subparsers.add_parser("export", help="Export as shell commands")
    p.set_defaults(func=cmd_export)

    # Diff
    p = subparsers.add_parser("diff", help="Compare two .env files")
    p.add_argument("file1", help="First file")
    p.add_argument("file2", help="Second file")
    p.set_defaults(func=cmd_diff)

    # Merge
    p = subparsers.add_parser("merge", help="Merge .env files")
    p.add_argument("files", nargs="+", help="Files to merge")
    p.add_argument("-o", "--output", help="Output file")
    p.set_defaults(func=cmd_merge)

    # Template
    p = subparsers.add_parser("template", aliases=["init"], help="Create from template")
    p.add_argument("template", help="Template file (e.g., .env.example)")
    p.add_argument("-o", "--output", default=".env", help="Output file")
    p.add_argument("-i", "--interactive", action="store_true", help="Prompt for values")
    p.set_defaults(func=cmd_template)

    # Validate
    p = subparsers.add_parser("validate", help="Validate required variables")
    p.add_argument("required", nargs="+", help="Required variable names")
    p.set_defaults(func=cmd_validate)

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
