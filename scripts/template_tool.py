#!/usr/bin/env python3
"""Template rendering with variable substitution."""

import argparse
import json
import os
import re
import sys
from pathlib import Path as PathLib
from string import Template

# Add parent directory to path to import utils
sys.path.insert(0, str(PathLib(__file__).parent.parent))

from utils import Path, Terminal


def parse_variables(var_args: list[str] | None) -> dict[str, str]:
    """Parse variable arguments (key=value format)."""
    variables = {}
    if var_args:
        for var in var_args:
            if "=" in var:
                key, value = var.split("=", 1)
                variables[key.strip()] = value.strip()
    return variables


def load_variables_from_file(file_path: str) -> dict:
    """Load variables from JSON or env file."""
    content = Path.read(file_path)

    if file_path.endswith(".json"):
        return json.loads(content)
    else:
        # Parse as .env format
        variables = {}
        for line in content.splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                key, value = line.split("=", 1)
                value = value.strip().strip('"\'')
                variables[key.strip()] = value
        return variables


def render_template(template: str, variables: dict, style: str = "dollar") -> str:
    """Render template with variables."""
    if style == "dollar":
        # $var or ${var} style
        t = Template(template)
        return t.safe_substitute(variables)

    elif style == "jinja":
        # {{ var }} style
        def replace(match):
            var_name = match.group(1).strip()
            return str(variables.get(var_name, match.group(0)))

        return re.sub(r"\{\{\s*(\w+)\s*\}\}", replace, template)

    elif style == "mustache":
        # {{var}} style (no spaces)
        def replace(match):
            var_name = match.group(1)
            return str(variables.get(var_name, match.group(0)))

        return re.sub(r"\{\{(\w+)\}\}", replace, template)

    elif style == "percent":
        # %(var)s style
        try:
            return template % variables
        except KeyError:
            # Safe substitute
            def replace(match):
                var_name = match.group(1)
                return str(variables.get(var_name, match.group(0)))
            return re.sub(r"%\((\w+)\)s", replace, template)

    elif style == "env":
        # ${VAR} or $VAR style, also check environment
        def replace(match):
            var_name = match.group(1) or match.group(2)
            return str(
                variables.get(var_name)
                or os.environ.get(var_name)
                or match.group(0)
            )

        result = re.sub(r"\$\{(\w+)\}|\$(\w+)", replace, template)
        return result

    return template


def cmd_render(args: argparse.Namespace) -> int:
    """Render a template."""
    # Load template
    template = Path.read(args.template)

    # Collect variables
    variables = {}

    # From environment
    if args.env:
        variables.update(os.environ)

    # From file
    if args.vars_file:
        variables.update(load_variables_from_file(args.vars_file))

    # From command line
    variables.update(parse_variables(args.var))

    # Render
    result = render_template(template, variables, args.style)

    # Output
    if args.output:
        Path.write(args.output, content=result)
        print(Terminal.colorize(f"Rendered to {args.output}", color="green"), file=sys.stderr)
    else:
        print(result)

    return 0


def cmd_variables(args: argparse.Namespace) -> int:
    """List variables in a template."""
    template = Path.read(args.template)

    patterns = {
        "dollar": r"\$\{?(\w+)\}?",
        "jinja": r"\{\{\s*(\w+)\s*\}\}",
        "mustache": r"\{\{(\w+)\}\}",
        "percent": r"%\((\w+)\)s",
        "env": r"\$\{(\w+)\}|\$(\w+)",
    }

    all_vars = set()
    for style, pattern in patterns.items():
        matches = re.findall(pattern, template)
        for match in matches:
            if isinstance(match, tuple):
                all_vars.update(m for m in match if m)
            else:
                all_vars.add(match)

    if all_vars:
        print(f"\n{Terminal.colorize('Template Variables', color='cyan', bold=True)}")
        Terminal.print_line("─", width=40)
        for var in sorted(all_vars):
            env_value = os.environ.get(var)
            if env_value:
                print(f"  {var} = {Terminal.colorize(env_value, color='green')} (from env)")
            else:
                print(f"  {var}")
    else:
        print(Terminal.colorize("No variables found", color="yellow"))

    return 0


def cmd_validate(args: argparse.Namespace) -> int:
    """Validate that all variables are provided."""
    template = Path.read(args.template)

    # Find all variables
    patterns = [
        r"\$\{(\w+)\}",
        r"\$(\w+)",
        r"\{\{\s*(\w+)\s*\}\}",
        r"%\((\w+)\)s",
    ]

    all_vars = set()
    for pattern in patterns:
        matches = re.findall(pattern, template)
        all_vars.update(matches)

    # Collect provided variables
    provided = set()

    if args.env:
        provided.update(os.environ.keys())

    if args.vars_file:
        provided.update(load_variables_from_file(args.vars_file).keys())

    provided.update(parse_variables(args.var).keys())

    # Check for missing
    missing = all_vars - provided

    if missing:
        print(Terminal.colorize("Missing variables:", color="red"))
        for var in sorted(missing):
            print(f"  - {var}")
        return 1
    else:
        print(Terminal.colorize("All variables provided", color="green"))
        return 0


def cmd_inline(args: argparse.Namespace) -> int:
    """Render inline template string."""
    variables = {}

    if args.env:
        variables.update(os.environ)

    if args.vars_file:
        variables.update(load_variables_from_file(args.vars_file))

    variables.update(parse_variables(args.var))

    result = render_template(args.template, variables, args.style)
    print(result)

    return 0


def cmd_create(args: argparse.Namespace) -> int:
    """Create template from existing file."""
    content = Path.read(args.source)

    # Replace values with variables
    for var in args.var or []:
        if "=" in var:
            name, value = var.split("=", 1)
            if args.style == "jinja":
                placeholder = f"{{{{ {name} }}}}"
            elif args.style == "mustache":
                placeholder = f"{{{{{name}}}}}"
            elif args.style == "percent":
                placeholder = f"%({name})s"
            else:
                placeholder = f"${{{name}}}"

            content = content.replace(value, placeholder)

    if args.output:
        Path.write(args.output, content=content)
        print(Terminal.colorize(f"Created template: {args.output}", color="green"))
    else:
        print(content)

    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Template tool - render templates with variable substitution.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Render template with variables
  python template_tool.py render template.txt -v name=John -v greeting=Hello
  # Template: ${greeting}, ${name}!
  # Output: Hello, John!

  # Load variables from file
  python template_tool.py render template.txt -f vars.json
  python template_tool.py render template.txt -f .env

  # Include environment variables
  python template_tool.py render config.template -e
  # Uses $HOME, $USER, etc.

  # Combine sources (later values override)
  python template_tool.py render app.conf -f defaults.json -f local.json -v debug=true

  # Save to output file
  python template_tool.py render template.txt -v name=World -o output.txt

  # Different template styles
  python template_tool.py -s dollar render tpl.txt -v var=value   # ${var} or $var
  python template_tool.py -s jinja render tpl.txt -v var=value    # {{ var }}
  python template_tool.py -s mustache render tpl.txt -v var=value # {{var}}
  python template_tool.py -s percent render tpl.txt -v var=value  # %%(var)s
  python template_tool.py -s env render tpl.txt -e                # ${VAR} + env

  # List variables in template
  python template_tool.py vars template.txt
  # Output: name, greeting, date (shows env values if set)

  # Validate all variables are provided
  python template_tool.py validate template.txt -v name=John
  # Output: ✓ All variables provided
  # OR:     Missing variables: greeting, date

  # Render inline template string
  python template_tool.py inline "Hello \\${name}!" -v name=World
  # Output: Hello World!

  # Create template from existing file
  python template_tool.py create config.ini -v db_host=localhost -v db_port=5432 -o config.template
  # Replaces "localhost" with ${db_host} and "5432" with ${db_port}

Variable styles:
  dollar:   ${var} or $var    (default, Python string.Template)
  jinja:    {{ var }}         (Jinja2-style with spaces)
  mustache: {{var}}           (Mustache-style, no spaces)
  percent:  %%(var)s          (Python %% formatting)
  env:      ${VAR}            (also checks environment)
""",
    )
    parser.add_argument(
        "-s", "--style",
        choices=["dollar", "jinja", "mustache", "percent", "env"],
        default="dollar",
        help="Variable style (default: dollar)",
    )
    subparsers = parser.add_subparsers(dest="command", help="Command")

    # Render
    p = subparsers.add_parser("render", aliases=["r"], help="Render template")
    p.add_argument("template", help="Template file")
    p.add_argument("-v", "--var", action="append", help="Variable (key=value)")
    p.add_argument("-f", "--vars-file", help="Variables file (JSON or .env)")
    p.add_argument("-e", "--env", action="store_true", help="Include environment variables")
    p.add_argument("-o", "--output", help="Output file")
    p.set_defaults(func=cmd_render)

    # Variables
    p = subparsers.add_parser("vars", aliases=["v"], help="List template variables")
    p.add_argument("template", help="Template file")
    p.set_defaults(func=cmd_variables)

    # Validate
    p = subparsers.add_parser("validate", help="Validate all variables provided")
    p.add_argument("template", help="Template file")
    p.add_argument("-v", "--var", action="append", help="Variable (key=value)")
    p.add_argument("-f", "--vars-file", help="Variables file")
    p.add_argument("-e", "--env", action="store_true", help="Include environment variables")
    p.set_defaults(func=cmd_validate)

    # Inline
    p = subparsers.add_parser("inline", aliases=["i"], help="Render inline template")
    p.add_argument("template", help="Template string")
    p.add_argument("-v", "--var", action="append", help="Variable (key=value)")
    p.add_argument("-f", "--vars-file", help="Variables file")
    p.add_argument("-e", "--env", action="store_true", help="Include environment variables")
    p.set_defaults(func=cmd_inline)

    # Create
    p = subparsers.add_parser("create", help="Create template from file")
    p.add_argument("source", help="Source file")
    p.add_argument("-v", "--var", action="append", help="Value to replace (name=value)")
    p.add_argument("-o", "--output", help="Output template file")
    p.set_defaults(func=cmd_create)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 0

    try:
        return args.func(args)
    except FileNotFoundError as e:
        print(Terminal.colorize(f"File not found: {e}", color="red"), file=sys.stderr)
        return 1
    except Exception as e:
        print(Terminal.colorize(f"Error: {e}", color="red"), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
