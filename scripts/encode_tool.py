#!/usr/bin/env python3
"""Encode/decode - base64, URL, HTML, hashing."""

import argparse
import sys
from pathlib import Path as PathLib

# Add parent directory to path to import utils
sys.path.insert(0, str(PathLib(__file__).parent.parent))

from utils import Decode, Encode, Hash, Path, Terminal


def read_input(file_path: str | None, text: str | None = None) -> str:
    """Read input from text arg, file, or stdin."""
    if text:
        return text
    if file_path:
        return Path.read(file_path)
    return sys.stdin.read().rstrip("\n")


def write_output(data: str, output: str | None, newline: bool = True) -> None:
    """Write output to file or stdout."""
    if output:
        Path.write(output, content=data)
        print(Terminal.colorize(f"Written to {output}", color="green"), file=sys.stderr)
    else:
        if newline:
            print(data)
        else:
            print(data, end="")


# Base64
def cmd_base64_encode(args: argparse.Namespace) -> int:
    """Encode to base64."""
    text = read_input(args.file, args.text)
    result = Encode.base64(text)
    write_output(result, args.output)
    return 0


def cmd_base64_decode(args: argparse.Namespace) -> int:
    """Decode from base64."""
    text = read_input(args.file, args.text)
    result = Decode.base64(text)
    write_output(result, args.output)
    return 0


# URL
def cmd_url_encode(args: argparse.Namespace) -> int:
    """URL encode."""
    text = read_input(args.file, args.text)
    result = Encode.url(text)
    write_output(result, args.output)
    return 0


def cmd_url_decode(args: argparse.Namespace) -> int:
    """URL decode."""
    text = read_input(args.file, args.text)
    result = Decode.url(text)
    write_output(result, args.output)
    return 0


# HTML
def cmd_html_encode(args: argparse.Namespace) -> int:
    """HTML encode."""
    text = read_input(args.file, args.text)
    result = Encode.html(text)
    write_output(result, args.output)
    return 0


def cmd_html_decode(args: argparse.Namespace) -> int:
    """HTML decode."""
    text = read_input(args.file, args.text)
    result = Decode.html(text)
    write_output(result, args.output)
    return 0


# Defang/Fang
def cmd_defang(args: argparse.Namespace) -> int:
    """Defang URLs/IPs for safe sharing."""
    text = read_input(args.file, args.text)
    result = Encode.defang(text)
    write_output(result, args.output)
    return 0


def cmd_fang(args: argparse.Namespace) -> int:
    """Refang defanged URLs/IPs."""
    text = read_input(args.file, args.text)
    result = Decode.fang(text)
    write_output(result, args.output)
    return 0


# Hashing
def cmd_hash(args: argparse.Namespace) -> int:
    """Hash text or file."""
    if args.file and PathLib(args.file).exists():
        # Hash file
        result = Hash.file(args.file, algorithm=args.algorithm)
    else:
        # Hash text
        text = read_input(args.file, args.text)
        if args.algorithm == "md5":
            result = Hash.md5(text)
        elif args.algorithm == "sha1":
            result = Hash.sha1(text)
        elif args.algorithm == "sha256":
            result = Hash.sha256(text)
        elif args.algorithm == "sha512":
            result = Hash.sha512(text)
        else:
            result = Hash.sha256(text)

    write_output(result, args.output)
    return 0


def cmd_verify(args: argparse.Namespace) -> int:
    """Verify hash."""
    if PathLib(args.file).exists():
        computed = Hash.file(args.file)
        import hmac
        result = hmac.compare_digest(computed, args.hash)
    else:
        result = Hash.verify(args.file, args.hash)

    if result:
        print(Terminal.colorize("✓ Hash verified", color="green"))
        return 0
    else:
        print(Terminal.colorize("✗ Hash mismatch", color="red"))
        return 1


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Encode/decode tool - base64, URL, HTML, hashing, defang/fang.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Base64 encode/decode
  python encode_tool.py b64 "Hello World"
  # Output: SGVsbG8gV29ybGQ=

  python encode_tool.py b64d "SGVsbG8gV29ybGQ="
  # Output: Hello World

  echo "secret data" | python encode_tool.py b64
  # Output: c2VjcmV0IGRhdGEK

  # URL encode/decode
  python encode_tool.py url "hello world & stuff"
  # Output: hello%20world%20%26%20stuff

  python encode_tool.py urld "hello%20world"
  # Output: hello world

  # HTML encode/decode (for safe embedding in HTML)
  python encode_tool.py html "<script>alert('xss')</script>"
  # Output: &lt;script&gt;alert(&#x27;xss&#x27;)&lt;/script&gt;

  python encode_tool.py htmld "&lt;p&gt;text&lt;/p&gt;"
  # Output: <p>text</p>

  # Defang URLs/IPs for safe sharing (prevents accidental clicks)
  python encode_tool.py defang "https://malicious.com/path"
  # Output: hxxps://malicious[.]com/path

  python encode_tool.py defang "192.168.1.1"
  # Output: 192[.]168[.]1[.]1

  # Refang (restore original URLs/IPs)
  python encode_tool.py fang "hxxps://example[.]com"
  # Output: https://example.com

  # Hash text or files
  python encode_tool.py hash "password123"
  # Output: ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f

  python encode_tool.py hash -a md5 "test"
  # Output: 098f6bcd4621d373cade4e832627b4f6

  python encode_tool.py hash -a sha512 myfile.txt
  # Output: (SHA-512 hash of file contents)

  # Verify hash
  python encode_tool.py verify "test" "098f6bcd4621d373cade4e832627b4f6"
  # Output: ✓ Hash verified

  python encode_tool.py verify myfile.txt "abc123..."
  # Output: ✗ Hash mismatch (exit code 1)

  # Read from file, write to file
  python encode_tool.py b64 -f input.txt -o encoded.txt
""",
    )
    subparsers = parser.add_subparsers(dest="command", help="Command")

    # Base64 encode
    p = subparsers.add_parser("b64", aliases=["base64"], help="Base64 encode")
    p.add_argument("text", nargs="?", help="Text to encode")
    p.add_argument("-f", "--file", help="Input file")
    p.add_argument("-o", "--output", help="Output file")
    p.set_defaults(func=cmd_base64_encode)

    # Base64 decode
    p = subparsers.add_parser("b64d", aliases=["base64d"], help="Base64 decode")
    p.add_argument("text", nargs="?", help="Text to decode")
    p.add_argument("-f", "--file", help="Input file")
    p.add_argument("-o", "--output", help="Output file")
    p.set_defaults(func=cmd_base64_decode)

    # URL encode
    p = subparsers.add_parser("url", help="URL encode")
    p.add_argument("text", nargs="?", help="Text to encode")
    p.add_argument("-f", "--file", help="Input file")
    p.add_argument("-o", "--output", help="Output file")
    p.set_defaults(func=cmd_url_encode)

    # URL decode
    p = subparsers.add_parser("urld", help="URL decode")
    p.add_argument("text", nargs="?", help="Text to decode")
    p.add_argument("-f", "--file", help="Input file")
    p.add_argument("-o", "--output", help="Output file")
    p.set_defaults(func=cmd_url_decode)

    # HTML encode
    p = subparsers.add_parser("html", help="HTML encode")
    p.add_argument("text", nargs="?", help="Text to encode")
    p.add_argument("-f", "--file", help="Input file")
    p.add_argument("-o", "--output", help="Output file")
    p.set_defaults(func=cmd_html_encode)

    # HTML decode
    p = subparsers.add_parser("htmld", help="HTML decode")
    p.add_argument("text", nargs="?", help="Text to decode")
    p.add_argument("-f", "--file", help="Input file")
    p.add_argument("-o", "--output", help="Output file")
    p.set_defaults(func=cmd_html_decode)

    # Defang
    p = subparsers.add_parser("defang", help="Defang URLs/IPs")
    p.add_argument("text", nargs="?", help="Text to defang")
    p.add_argument("-f", "--file", help="Input file")
    p.add_argument("-o", "--output", help="Output file")
    p.set_defaults(func=cmd_defang)

    # Fang
    p = subparsers.add_parser("fang", help="Refang URLs/IPs")
    p.add_argument("text", nargs="?", help="Text to fang")
    p.add_argument("-f", "--file", help="Input file")
    p.add_argument("-o", "--output", help="Output file")
    p.set_defaults(func=cmd_fang)

    # Hash
    p = subparsers.add_parser("hash", help="Hash text or file")
    p.add_argument("text", nargs="?", help="Text to hash (or file path)")
    p.add_argument("-f", "--file", help="Input file")
    p.add_argument(
        "-a",
        "--algorithm",
        choices=["md5", "sha1", "sha256", "sha512"],
        default="sha256",
        help="Algorithm (default: sha256)",
    )
    p.add_argument("-o", "--output", help="Output file")
    p.set_defaults(func=cmd_hash)

    # Verify
    p = subparsers.add_parser("verify", help="Verify hash")
    p.add_argument("file", help="Text or file to verify")
    p.add_argument("hash", help="Expected hash")
    p.set_defaults(func=cmd_verify)

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
