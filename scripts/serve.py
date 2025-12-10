#!/usr/bin/env python3
"""Quick local HTTP server with directory listing."""

import argparse
import html
import mimetypes
import os
import socket
import sys
import urllib.parse
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path as PathLib

# Add parent directory to path to import utils
sys.path.insert(0, str(PathLib(__file__).parent.parent))

from utils import Terminal


class CustomHandler(SimpleHTTPRequestHandler):
    """Custom HTTP handler with better features."""

    def __init__(self, *args, directory=None, cors=False, **kwargs):
        self.cors = cors
        super().__init__(*args, directory=directory, **kwargs)

    def end_headers(self):
        if self.cors:
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
            self.send_header("Access-Control-Allow-Headers", "*")
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def log_message(self, format, *args):
        status = args[1] if len(args) > 1 else "200"
        method = args[0].split()[0] if args else "GET"

        if status.startswith("2"):
            status_color = "green"
        elif status.startswith("3"):
            status_color = "cyan"
        elif status.startswith("4"):
            status_color = "yellow"
        else:
            status_color = "red"

        print(
            f"{Terminal.colorize(method, color='cyan')} "
            f"{Terminal.colorize(status, color=status_color)} "
            f"{args[0].split()[1] if args else '/'}"
        )

    def list_directory(self, path):
        """Generate directory listing with better styling."""
        try:
            entries = os.listdir(path)
        except OSError:
            self.send_error(404, "No permission to list directory")
            return None

        entries.sort(key=lambda a: (not os.path.isdir(os.path.join(path, a)), a.lower()))

        display_path = urllib.parse.unquote(self.path)
        title = f"Directory: {html.escape(display_path)}"

        content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>{title}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            max-width: 900px;
            margin: 40px auto;
            padding: 0 20px;
            background: #f5f5f5;
        }}
        h1 {{
            color: #333;
            border-bottom: 2px solid #007acc;
            padding-bottom: 10px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            background: white;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }}
        th, td {{
            padding: 12px 15px;
            text-align: left;
            border-bottom: 1px solid #eee;
        }}
        th {{
            background: #007acc;
            color: white;
        }}
        tr:hover {{
            background: #f8f8f8;
        }}
        a {{
            color: #007acc;
            text-decoration: none;
        }}
        a:hover {{
            text-decoration: underline;
        }}
        .folder {{
            color: #e67e22;
        }}
        .size {{
            color: #666;
            font-size: 0.9em;
        }}
    </style>
</head>
<body>
    <h1>{title}</h1>
    <table>
        <tr>
            <th>Name</th>
            <th>Size</th>
            <th>Type</th>
        </tr>
"""

        if display_path != "/":
            content += """
        <tr>
            <td><a href="..">..</a></td>
            <td></td>
            <td>Parent Directory</td>
        </tr>
"""

        for name in entries:
            if name.startswith("."):
                continue

            fullpath = os.path.join(path, name)
            display_name = name

            if os.path.isdir(fullpath):
                display_name = name + "/"
                size = "-"
                file_type = "Directory"
                css_class = "folder"
            else:
                size = self._format_size(os.path.getsize(fullpath))
                file_type = mimetypes.guess_type(name)[0] or "File"
                css_class = ""

            link = urllib.parse.quote(name, safe="")
            if os.path.isdir(fullpath):
                link += "/"

            content += f"""
        <tr>
            <td><a class="{css_class}" href="{link}">{html.escape(display_name)}</a></td>
            <td class="size">{size}</td>
            <td>{file_type}</td>
        </tr>
"""

        content += """
    </table>
</body>
</html>
"""

        encoded = content.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        return encoded

    def _format_size(self, size):
        for unit in ["B", "KB", "MB", "GB"]:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"


def find_free_port(start_port: int, host: str = "localhost") -> int:
    """Find a free port starting from start_port."""
    port = start_port
    while port < start_port + 100:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind((host, port))
                return port
        except OSError:
            port += 1
    return start_port


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Quick local HTTP server with directory listing and CORS support.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Serve current directory on port 8000
  python serve.py
  # Opens browser to http://localhost:8000

  # Serve specific directory
  python serve.py ./dist
  python serve.py ~/Documents/project/build

  # Use custom port
  python serve.py -p 3000
  python serve.py ./public -p 8080

  # Bind to all interfaces (accessible from network)
  python serve.py -b 0.0.0.0
  # Access from other devices: http://192.168.1.x:8000

  # Enable CORS (for API/frontend development)
  python serve.py ./api --cors
  # Adds Access-Control-Allow-Origin: * headers

  # Don't open browser automatically
  python serve.py --no-browser

  # Full example for frontend development
  python serve.py ./dist -p 3000 --cors

  # Serve for mobile device testing
  python serve.py -b 0.0.0.0 -p 8000

Features:
  - Styled directory listing with file sizes and types
  - Automatic port finding if specified port is busy
  - Colored request logging (green=2xx, cyan=3xx, yellow=4xx, red=5xx)
  - Optional CORS headers for API/frontend development
""",
    )
    parser.add_argument("directory", nargs="?", default=".", help="Directory to serve")
    parser.add_argument("-p", "--port", type=int, default=8000, help="Port (default: 8000)")
    parser.add_argument("-b", "--bind", default="localhost", help="Bind address")
    parser.add_argument("--cors", action="store_true", help="Enable CORS")
    parser.add_argument("--no-browser", action="store_true", help="Don't open browser")
    args = parser.parse_args()

    directory = PathLib(args.directory).resolve()
    if not directory.is_dir():
        print(Terminal.colorize(f"Not a directory: {args.directory}", color="red"))
        return 1

    # Find available port
    port = find_free_port(args.port, args.bind)
    if port != args.port:
        print(Terminal.colorize(f"Port {args.port} in use, using {port}", color="yellow"))

    # Create handler class with directory
    def handler_class(*handler_args, **handler_kwargs):
        return CustomHandler(
            *handler_args,
            directory=str(directory),
            cors=args.cors,
            **handler_kwargs,
        )

    server = HTTPServer((args.bind, port), handler_class)

    url = f"http://{args.bind}:{port}"
    print()
    Terminal.print_box(f"Serving: {directory}")
    print()
    print(f"  URL: {Terminal.colorize(url, color='cyan', bold=True)}")
    print(f"  CORS: {'enabled' if args.cors else 'disabled'}")
    print()
    print(Terminal.colorize("Press Ctrl+C to stop", color="yellow"))
    Terminal.print_line("═", width=60)
    print()

    # Open browser
    if not args.no_browser:
        import webbrowser
        webbrowser.open(url)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print(Terminal.colorize("\n\nServer stopped", color="yellow"))
        return 0


if __name__ == "__main__":
    sys.exit(main())
