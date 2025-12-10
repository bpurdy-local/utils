#!/usr/bin/env python3
"""Create and extract archives - zip, tar, gzip."""

import argparse
import gzip
import os
import shutil
import sys
import tarfile
import zipfile
from pathlib import Path as PathLib

# Add parent directory to path to import utils
sys.path.insert(0, str(PathLib(__file__).parent.parent))

from utils import Terminal


def get_archive_type(filename: str) -> str:
    """Determine archive type from filename."""
    name = filename.lower()
    if name.endswith(".zip"):
        return "zip"
    elif name.endswith(".tar.gz") or name.endswith(".tgz"):
        return "tar.gz"
    elif name.endswith(".tar.bz2") or name.endswith(".tbz2"):
        return "tar.bz2"
    elif name.endswith(".tar.xz") or name.endswith(".txz"):
        return "tar.xz"
    elif name.endswith(".tar"):
        return "tar"
    elif name.endswith(".gz"):
        return "gz"
    return "unknown"


def format_size(size: int) -> str:
    """Format file size."""
    for unit in ["B", "KB", "MB", "GB"]:
        if size < 1024:
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} TB"


def cmd_create(args: argparse.Namespace) -> int:
    """Create an archive."""
    output = args.output
    files = args.files

    # Determine archive type
    archive_type = args.type or get_archive_type(output)

    print(Terminal.colorize(f"Creating {archive_type} archive: {output}", color="cyan", bold=True))

    try:
        if archive_type == "zip":
            with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as zf:
                for file_path in files:
                    path = PathLib(file_path)
                    if path.is_dir():
                        for root, _, filenames in os.walk(path):
                            for filename in filenames:
                                full_path = PathLib(root) / filename
                                arcname = full_path.relative_to(path.parent)
                                print(f"  Adding: {arcname}")
                                zf.write(full_path, arcname)
                    else:
                        print(f"  Adding: {path.name}")
                        zf.write(path, path.name)

        elif archive_type in ("tar", "tar.gz", "tar.bz2", "tar.xz"):
            mode_map = {
                "tar": "w",
                "tar.gz": "w:gz",
                "tar.bz2": "w:bz2",
                "tar.xz": "w:xz",
            }
            with tarfile.open(output, mode_map[archive_type]) as tf:
                for file_path in files:
                    path = PathLib(file_path)
                    print(f"  Adding: {path}")
                    tf.add(path, arcname=path.name)

        elif archive_type == "gz":
            if len(files) != 1:
                print(Terminal.colorize("gzip only supports single file", color="red"))
                return 1
            with open(files[0], "rb") as f_in:
                with gzip.open(output, "wb") as f_out:
                    shutil.copyfileobj(f_in, f_out)

        else:
            print(Terminal.colorize(f"Unknown archive type: {archive_type}", color="red"))
            return 1

        size = os.path.getsize(output)
        print(Terminal.colorize(f"\nCreated: {output} ({format_size(size)})", color="green"))
        return 0

    except Exception as e:
        print(Terminal.colorize(f"Error: {e}", color="red"))
        return 1


def cmd_extract(args: argparse.Namespace) -> int:
    """Extract an archive."""
    archive = args.archive
    output = args.output or "."

    archive_type = get_archive_type(archive)

    print(Terminal.colorize(f"Extracting: {archive}", color="cyan", bold=True))
    print(f"Destination: {output}")
    print()

    try:
        os.makedirs(output, exist_ok=True)

        if archive_type == "zip":
            with zipfile.ZipFile(archive, "r") as zf:
                for name in zf.namelist():
                    print(f"  Extracting: {name}")
                zf.extractall(output)

        elif archive_type in ("tar", "tar.gz", "tar.bz2", "tar.xz"):
            with tarfile.open(archive, "r:*") as tf:
                for member in tf.getmembers():
                    print(f"  Extracting: {member.name}")
                tf.extractall(output)

        elif archive_type == "gz":
            out_name = PathLib(archive).stem
            out_path = PathLib(output) / out_name
            with gzip.open(archive, "rb") as f_in:
                with open(out_path, "wb") as f_out:
                    shutil.copyfileobj(f_in, f_out)
            print(f"  Extracted: {out_name}")

        else:
            print(Terminal.colorize(f"Unknown archive type: {archive_type}", color="red"))
            return 1

        print(Terminal.colorize("\nExtraction complete", color="green"))
        return 0

    except Exception as e:
        print(Terminal.colorize(f"Error: {e}", color="red"))
        return 1


def cmd_list(args: argparse.Namespace) -> int:
    """List archive contents."""
    archive = args.archive
    archive_type = get_archive_type(archive)

    print(Terminal.colorize(f"Contents of: {archive}", color="cyan", bold=True))
    Terminal.print_line("─", width=60)

    try:
        if archive_type == "zip":
            with zipfile.ZipFile(archive, "r") as zf:
                total_size = 0
                for info in zf.infolist():
                    size = format_size(info.file_size)
                    print(f"  {size:>10}  {info.filename}")
                    total_size += info.file_size
                print()
                print(f"Total: {len(zf.infolist())} files, {format_size(total_size)}")

        elif archive_type in ("tar", "tar.gz", "tar.bz2", "tar.xz"):
            with tarfile.open(archive, "r:*") as tf:
                total_size = 0
                count = 0
                for member in tf.getmembers():
                    size = format_size(member.size) if member.isfile() else "<DIR>"
                    print(f"  {size:>10}  {member.name}")
                    total_size += member.size
                    count += 1
                print()
                print(f"Total: {count} items, {format_size(total_size)}")

        else:
            print(Terminal.colorize(f"Unknown archive type: {archive_type}", color="red"))
            return 1

        return 0

    except Exception as e:
        print(Terminal.colorize(f"Error: {e}", color="red"))
        return 1


def cmd_test(args: argparse.Namespace) -> int:
    """Test archive integrity."""
    archive = args.archive
    archive_type = get_archive_type(archive)

    print(Terminal.colorize(f"Testing: {archive}", color="cyan", bold=True))

    try:
        if archive_type == "zip":
            with zipfile.ZipFile(archive, "r") as zf:
                bad_file = zf.testzip()
                if bad_file:
                    print(Terminal.colorize(f"Corrupted file: {bad_file}", color="red"))
                    return 1

        elif archive_type in ("tar", "tar.gz", "tar.bz2", "tar.xz"):
            with tarfile.open(archive, "r:*") as tf:
                # Try to read each member
                for member in tf.getmembers():
                    if member.isfile():
                        tf.extractfile(member).read()

        else:
            print(Terminal.colorize(f"Unknown archive type: {archive_type}", color="red"))
            return 1

        print(Terminal.colorize("Archive is OK", color="green"))
        return 0

    except Exception as e:
        print(Terminal.colorize(f"Archive corrupted: {e}", color="red"))
        return 1


def cmd_add(args: argparse.Namespace) -> int:
    """Add files to existing archive."""
    archive = args.archive
    files = args.files
    archive_type = get_archive_type(archive)

    if archive_type != "zip":
        print(Terminal.colorize("Adding to archive only supported for zip", color="yellow"))
        return 1

    try:
        with zipfile.ZipFile(archive, "a") as zf:
            for file_path in files:
                path = PathLib(file_path)
                print(f"  Adding: {path.name}")
                zf.write(path, path.name)

        print(Terminal.colorize("Files added", color="green"))
        return 0

    except Exception as e:
        print(Terminal.colorize(f"Error: {e}", color="red"))
        return 1


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Archive tool - create and extract zip, tar, gzip archives.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Create a zip archive
  python archive_tool.py create backup.zip file1.txt file2.txt
  python archive_tool.py create project.zip src/ tests/ README.md

  # Create tar.gz archive
  python archive_tool.py create backup.tar.gz mydir/
  python archive_tool.py create data.tgz *.csv

  # Create with explicit type
  python archive_tool.py create backup.archive src/ -t tar.bz2

  # Extract archive (auto-detects type)
  python archive_tool.py extract backup.zip
  python archive_tool.py extract data.tar.gz

  # Extract to specific directory
  python archive_tool.py extract backup.zip -o ./extracted/

  # List archive contents
  python archive_tool.py list backup.zip
  # Output:   10.5 KB  file1.txt
  #            2.3 KB  file2.txt
  #           Total: 2 files, 12.8 KB

  python archive_tool.py list project.tar.gz

  # Test archive integrity
  python archive_tool.py test backup.zip
  # Output: Archive is OK

  # Add files to existing zip
  python archive_tool.py add backup.zip newfile.txt

Supported formats:
  .zip           - ZIP archive
  .tar           - TAR archive (uncompressed)
  .tar.gz, .tgz  - TAR with gzip compression
  .tar.bz2, .tbz2 - TAR with bzip2 compression
  .tar.xz, .txz  - TAR with xz compression
  .gz            - Single file gzip compression
""",
    )
    subparsers = parser.add_subparsers(dest="command", help="Command")

    # Create
    p = subparsers.add_parser("create", aliases=["c"], help="Create archive")
    p.add_argument("output", help="Output archive name")
    p.add_argument("files", nargs="+", help="Files/directories to add")
    p.add_argument(
        "-t", "--type",
        choices=["zip", "tar", "tar.gz", "tar.bz2", "tar.xz", "gz"],
        help="Archive type (auto-detected from extension)",
    )
    p.set_defaults(func=cmd_create)

    # Extract
    p = subparsers.add_parser("extract", aliases=["x"], help="Extract archive")
    p.add_argument("archive", help="Archive to extract")
    p.add_argument("-o", "--output", help="Output directory")
    p.set_defaults(func=cmd_extract)

    # List
    p = subparsers.add_parser("list", aliases=["l", "ls"], help="List contents")
    p.add_argument("archive", help="Archive to list")
    p.set_defaults(func=cmd_list)

    # Test
    p = subparsers.add_parser("test", aliases=["t"], help="Test integrity")
    p.add_argument("archive", help="Archive to test")
    p.set_defaults(func=cmd_test)

    # Add
    p = subparsers.add_parser("add", aliases=["a"], help="Add files to archive")
    p.add_argument("archive", help="Archive to add to")
    p.add_argument("files", nargs="+", help="Files to add")
    p.set_defaults(func=cmd_add)

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
