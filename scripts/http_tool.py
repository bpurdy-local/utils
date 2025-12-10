#!/usr/bin/env python3
"""Quick HTTP requests - GET, POST, headers, auth, save responses."""

import argparse
import json
import sys
from pathlib import Path as PathLib

# Add parent directory to path to import utils
sys.path.insert(0, str(PathLib(__file__).parent.parent))

from utils import JSON, Path, Session, Terminal


def parse_headers(header_args: list[str] | None) -> dict[str, str]:
    """Parse header arguments into dict."""
    headers = {}
    if header_args:
        for h in header_args:
            if ":" in h:
                key, value = h.split(":", 1)
                headers[key.strip()] = value.strip()
    return headers


def parse_data(data_arg: str | None, json_arg: str | None, form: bool = False) -> tuple:
    """Parse data arguments. Returns (data, json_data)."""
    if json_arg:
        return None, json.loads(json_arg)
    if data_arg:
        if form:
            # Parse as form data: key=value&key2=value2
            pairs = data_arg.split("&")
            return {k: v for k, v in (p.split("=", 1) for p in pairs)}, None
        return data_arg, None
    return None, None


def format_response(response, verbose: bool = False, headers_only: bool = False) -> str:
    """Format response for output."""
    lines = []

    if verbose or headers_only:
        lines.append(Terminal.colorize(f"HTTP {response.status_code} {response.reason}",
                                        color="green" if response.ok else "red", bold=True))
        lines.append("")
        for key, value in response.headers.items():
            lines.append(f"{Terminal.colorize(key, color='cyan')}: {value}")
        lines.append("")

    if not headers_only:
        content_type = response.headers.get("content-type", "")
        if "application/json" in content_type:
            try:
                lines.append(JSON.pretty(response.text))
            except Exception:
                lines.append(response.text)
        else:
            lines.append(response.text)

    return "\n".join(lines)


def cmd_get(args: argparse.Namespace) -> int:
    """HTTP GET request."""
    session = Session(timeout=args.timeout)
    headers = parse_headers(args.header)

    if args.bearer:
        headers["Authorization"] = f"Bearer {args.bearer}"

    response = session.get(args.url, headers=headers, params=dict(args.query or []))

    output = format_response(response, args.verbose, args.headers)

    if args.output:
        Path.write(args.output, content=response.text)
        print(Terminal.colorize(f"Saved to {args.output}", color="green"), file=sys.stderr)
    else:
        print(output)

    return 0 if response.ok else 1


def cmd_post(args: argparse.Namespace) -> int:
    """HTTP POST request."""
    session = Session(timeout=args.timeout)
    headers = parse_headers(args.header)

    if args.bearer:
        headers["Authorization"] = f"Bearer {args.bearer}"

    data, json_data = parse_data(args.data, args.json, args.form)

    response = session.post(args.url, headers=headers, data=data, json=json_data)

    output = format_response(response, args.verbose, args.headers)

    if args.output:
        Path.write(args.output, content=response.text)
        print(Terminal.colorize(f"Saved to {args.output}", color="green"), file=sys.stderr)
    else:
        print(output)

    return 0 if response.ok else 1


def cmd_put(args: argparse.Namespace) -> int:
    """HTTP PUT request."""
    session = Session(timeout=args.timeout)
    headers = parse_headers(args.header)

    if args.bearer:
        headers["Authorization"] = f"Bearer {args.bearer}"

    data, json_data = parse_data(args.data, args.json, args.form)

    response = session.put(args.url, headers=headers, data=data, json=json_data)

    output = format_response(response, args.verbose, args.headers)
    print(output)

    return 0 if response.ok else 1


def cmd_delete(args: argparse.Namespace) -> int:
    """HTTP DELETE request."""
    session = Session(timeout=args.timeout)
    headers = parse_headers(args.header)

    if args.bearer:
        headers["Authorization"] = f"Bearer {args.bearer}"

    response = session.delete(args.url, headers=headers)

    output = format_response(response, args.verbose, args.headers)
    print(output)

    return 0 if response.ok else 1


def cmd_head(args: argparse.Namespace) -> int:
    """HTTP HEAD request."""
    session = Session(timeout=args.timeout)
    headers = parse_headers(args.header)

    response = session.head(args.url, headers=headers)

    print(Terminal.colorize(f"HTTP {response.status_code} {response.reason}",
                            color="green" if response.ok else "red", bold=True))
    print()
    for key, value in response.headers.items():
        print(f"{Terminal.colorize(key, color='cyan')}: {value}")

    return 0 if response.ok else 1


def cmd_download(args: argparse.Namespace) -> int:
    """Download file."""
    session = Session(timeout=args.timeout)
    headers = parse_headers(args.header)

    response = session.get(args.url, headers=headers, stream=True)

    if not response.ok:
        print(Terminal.colorize(f"Error: HTTP {response.status_code}", color="red"))
        return 1

    # Determine filename
    filename = args.output
    if not filename:
        # Try to get from Content-Disposition header
        cd = response.headers.get("content-disposition", "")
        if "filename=" in cd:
            filename = cd.split("filename=")[1].strip('"')
        else:
            # Use last part of URL
            filename = args.url.split("/")[-1].split("?")[0] or "download"

    total = int(response.headers.get("content-length", 0))
    downloaded = 0

    with open(filename, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
            downloaded += len(chunk)
            if total:
                progress = Terminal.progress_bar(downloaded, total, width=40)
                print(f"\r{progress}", end="", file=sys.stderr)

    print(file=sys.stderr)
    print(Terminal.colorize(f"Downloaded: {filename}", color="green"))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="HTTP request tool - GET, POST, PUT, DELETE, download files.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Simple GET request
  python http_tool.py get https://api.example.com/users
  # Output: JSON response (auto-formatted)

  # GET with query parameters
  python http_tool.py get https://api.example.com/search -q term "hello" -q limit 10

  # GET with custom headers
  python http_tool.py get https://api.example.com/data -H "X-Custom: value"

  # GET with Bearer token authentication
  python http_tool.py get https://api.example.com/protected -b "your-jwt-token"

  # Show response headers (-v) or headers only (--headers)
  python http_tool.py get https://api.example.com/data -v
  python http_tool.py get https://api.example.com/data --headers

  # Save response to file
  python http_tool.py get https://api.example.com/data -o response.json

  # POST with JSON body
  python http_tool.py post https://api.example.com/users -j '{"name": "John"}'

  # POST with form data
  python http_tool.py post https://api.example.com/login -d "user=john&pass=secret" -f

  # PUT and DELETE requests
  python http_tool.py put https://api.example.com/users/123 -j '{"name": "Updated"}'
  python http_tool.py delete https://api.example.com/users/123

  # HEAD request (headers only)
  python http_tool.py head https://example.com

  # Download file with progress bar
  python http_tool.py download https://example.com/file.zip -o myfile.zip

  # Set custom timeout
  python http_tool.py -t 60 get https://slow-api.example.com/data
""",
    )
    parser.add_argument("-t", "--timeout", type=int, default=30, help="Timeout in seconds")
    subparsers = parser.add_subparsers(dest="command", help="Command")

    # GET
    p = subparsers.add_parser("get", help="GET request")
    p.add_argument("url", help="URL")
    p.add_argument("-H", "--header", action="append", help="Header (Key: Value)")
    p.add_argument("-q", "--query", nargs=2, action="append", metavar=("KEY", "VALUE"))
    p.add_argument("-b", "--bearer", help="Bearer token")
    p.add_argument("-v", "--verbose", action="store_true", help="Show headers")
    p.add_argument("--headers", action="store_true", help="Headers only")
    p.add_argument("-o", "--output", help="Save to file")
    p.set_defaults(func=cmd_get)

    # POST
    p = subparsers.add_parser("post", help="POST request")
    p.add_argument("url", help="URL")
    p.add_argument("-H", "--header", action="append", help="Header (Key: Value)")
    p.add_argument("-d", "--data", help="Request body")
    p.add_argument("-j", "--json", help="JSON body")
    p.add_argument("-f", "--form", action="store_true", help="Form data")
    p.add_argument("-b", "--bearer", help="Bearer token")
    p.add_argument("-v", "--verbose", action="store_true", help="Show headers")
    p.add_argument("--headers", action="store_true", help="Headers only")
    p.add_argument("-o", "--output", help="Save to file")
    p.set_defaults(func=cmd_post)

    # PUT
    p = subparsers.add_parser("put", help="PUT request")
    p.add_argument("url", help="URL")
    p.add_argument("-H", "--header", action="append", help="Header (Key: Value)")
    p.add_argument("-d", "--data", help="Request body")
    p.add_argument("-j", "--json", help="JSON body")
    p.add_argument("-f", "--form", action="store_true", help="Form data")
    p.add_argument("-b", "--bearer", help="Bearer token")
    p.add_argument("-v", "--verbose", action="store_true", help="Show headers")
    p.add_argument("--headers", action="store_true", help="Headers only")
    p.set_defaults(func=cmd_put)

    # DELETE
    p = subparsers.add_parser("delete", help="DELETE request")
    p.add_argument("url", help="URL")
    p.add_argument("-H", "--header", action="append", help="Header (Key: Value)")
    p.add_argument("-b", "--bearer", help="Bearer token")
    p.add_argument("-v", "--verbose", action="store_true", help="Show headers")
    p.add_argument("--headers", action="store_true", help="Headers only")
    p.set_defaults(func=cmd_delete)

    # HEAD
    p = subparsers.add_parser("head", help="HEAD request")
    p.add_argument("url", help="URL")
    p.add_argument("-H", "--header", action="append", help="Header (Key: Value)")
    p.set_defaults(func=cmd_head)

    # Download
    p = subparsers.add_parser("download", aliases=["dl"], help="Download file")
    p.add_argument("url", help="URL")
    p.add_argument("-o", "--output", help="Output filename")
    p.add_argument("-H", "--header", action="append", help="Header (Key: Value)")
    p.set_defaults(func=cmd_download)

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
