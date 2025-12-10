#!/usr/bin/env python3
"""IP utilities - lookup, info, ping, port check."""

import argparse
import ipaddress
import socket
import subprocess
import sys
from pathlib import Path as PathLib

# Add parent directory to path to import utils
sys.path.insert(0, str(PathLib(__file__).parent.parent))

from utils import Session, Terminal


def cmd_info(args: argparse.Namespace) -> int:
    """Get info about an IP address."""
    try:
        ip = ipaddress.ip_address(args.ip)
    except ValueError:
        # Try to resolve hostname
        try:
            ip = ipaddress.ip_address(socket.gethostbyname(args.ip))
            print(f"Resolved {args.ip} to {ip}")
        except socket.gaierror:
            print(Terminal.colorize(f"Invalid IP or hostname: {args.ip}", color="red"))
            return 1

    print(f"\n{Terminal.colorize('IP Information', color='cyan', bold=True)}")
    Terminal.print_line("─", width=40)
    print(f"Address: {ip}")
    print(f"Version: IPv{ip.version}")
    print(f"Type: {'Private' if ip.is_private else 'Public'}")
    print(f"Loopback: {ip.is_loopback}")
    print(f"Link-local: {ip.is_link_local}")
    print(f"Multicast: {ip.is_multicast}")
    print(f"Reserved: {ip.is_reserved}")

    if ip.version == 4:
        print(f"Binary: {'.'.join(format(b, '08b') for b in ip.packed)}")

    return 0


def cmd_lookup(args: argparse.Namespace) -> int:
    """Lookup IP geolocation (uses ip-api.com)."""
    session = Session(timeout=10)

    try:
        response = session.get(f"http://ip-api.com/json/{args.ip}")
        data = response.json()

        if data.get("status") == "fail":
            print(Terminal.colorize(f"Lookup failed: {data.get('message')}", color="red"))
            return 1

        print(f"\n{Terminal.colorize('IP Geolocation', color='cyan', bold=True)}")
        Terminal.print_line("─", width=40)
        print(f"IP: {data.get('query')}")
        print(f"Country: {data.get('country')} ({data.get('countryCode')})")
        print(f"Region: {data.get('regionName')} ({data.get('region')})")
        print(f"City: {data.get('city')}")
        print(f"ZIP: {data.get('zip')}")
        print(f"Timezone: {data.get('timezone')}")
        print(f"ISP: {data.get('isp')}")
        print(f"Org: {data.get('org')}")
        print(f"AS: {data.get('as')}")
        print(f"Coordinates: {data.get('lat')}, {data.get('lon')}")

        return 0
    except Exception as e:
        print(Terminal.colorize(f"Error: {e}", color="red"))
        return 1


def cmd_myip(args: argparse.Namespace) -> int:
    """Get your public IP."""
    session = Session(timeout=10)

    try:
        if args.v6:
            response = session.get("https://api6.ipify.org?format=json")
        else:
            response = session.get("https://api.ipify.org?format=json")

        data = response.json()
        ip = data.get("ip")

        if args.simple:
            print(ip)
        else:
            print(f"Your public IP: {Terminal.colorize(ip, color='green', bold=True)}")

            if args.lookup:
                # Also do geolocation
                args.ip = ip
                print()
                cmd_lookup(args)

        return 0
    except Exception as e:
        print(Terminal.colorize(f"Error: {e}", color="red"))
        return 1


def cmd_ping(args: argparse.Namespace) -> int:
    """Ping a host."""
    count = str(args.count)

    # Use appropriate ping command
    if sys.platform == "darwin":
        cmd = ["ping", "-c", count, args.host]
    elif sys.platform == "win32":
        cmd = ["ping", "-n", count, args.host]
    else:
        cmd = ["ping", "-c", count, args.host]

    print(f"Pinging {args.host}...")
    result = subprocess.run(cmd)
    return result.returncode


def cmd_port(args: argparse.Namespace) -> int:
    """Check if a port is open."""
    host = args.host
    ports = args.ports

    results = []
    for port in ports:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(args.timeout)
            result = sock.connect_ex((host, port))
            sock.close()

            if result == 0:
                status = Terminal.colorize("open", color="green")
                try:
                    service = socket.getservbyport(port)
                except OSError:
                    service = "unknown"
            else:
                status = Terminal.colorize("closed", color="red")
                service = ""

            results.append((port, status, service))
        except socket.gaierror:
            print(Terminal.colorize(f"Could not resolve: {host}", color="red"))
            return 1
        except Exception as e:
            results.append((port, Terminal.colorize("error", color="yellow"), str(e)))

    print(f"\n{Terminal.colorize(f'Port scan: {host}', color='cyan', bold=True)}")
    Terminal.print_line("─", width=40)
    for port, status, service in results:
        print(f"  {port:5d}  {status:20s}  {service}")

    return 0


def cmd_resolve(args: argparse.Namespace) -> int:
    """Resolve hostname to IP."""
    try:
        if args.all:
            # Get all addresses
            results = socket.getaddrinfo(args.hostname, None)
            ips = set()
            for result in results:
                ip = result[4][0]
                ips.add(ip)

            for ip in sorted(ips):
                print(ip)
        else:
            ip = socket.gethostbyname(args.hostname)
            print(ip)

        return 0
    except socket.gaierror as e:
        print(Terminal.colorize(f"Could not resolve: {e}", color="red"))
        return 1


def cmd_reverse(args: argparse.Namespace) -> int:
    """Reverse DNS lookup."""
    try:
        hostname, _, _ = socket.gethostbyaddr(args.ip)
        print(hostname)
        return 0
    except socket.herror:
        print(Terminal.colorize("No reverse DNS found", color="yellow"))
        return 1


def cmd_cidr(args: argparse.Namespace) -> int:
    """CIDR calculator."""
    try:
        network = ipaddress.ip_network(args.cidr, strict=False)

        print(f"\n{Terminal.colorize('CIDR Information', color='cyan', bold=True)}")
        Terminal.print_line("─", width=40)
        print(f"Network: {network.network_address}")
        print(f"Netmask: {network.netmask}")
        print(f"Broadcast: {network.broadcast_address}")
        print(f"Prefix: /{network.prefixlen}")
        print(f"Total hosts: {network.num_addresses}")
        print(f"Usable hosts: {max(0, network.num_addresses - 2)}")
        print(f"First host: {list(network.hosts())[0] if network.num_addresses > 2 else 'N/A'}")
        print(f"Last host: {list(network.hosts())[-1] if network.num_addresses > 2 else 'N/A'}")

        if args.list_hosts and network.num_addresses <= 256:
            print(f"\n{Terminal.colorize('Hosts:', color='cyan')}")
            for host in network.hosts():
                print(f"  {host}")

        return 0
    except ValueError as e:
        print(Terminal.colorize(f"Invalid CIDR: {e}", color="red"))
        return 1


def main() -> int:
    parser = argparse.ArgumentParser(
        description="IP utilities - lookup, geolocation, ping, port scanning, CIDR calculator.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Get info about an IP address
  python ip_tool.py info 8.8.8.8
  # Output: Version: IPv4, Type: Public, Loopback: False, ...

  # Get info from hostname
  python ip_tool.py info google.com
  # Resolves and shows IP info

  # IP geolocation lookup
  python ip_tool.py lookup 8.8.8.8
  # Output: Country: United States, City: Mountain View, ISP: Google, ...

  # Get your public IP
  python ip_tool.py myip
  # Output: Your public IP: 203.x.x.x

  # Get just the IP (for scripting)
  python ip_tool.py myip -s
  # Output: 203.x.x.x

  # Get your IP with geolocation
  python ip_tool.py myip -l

  # Get IPv6 address
  python ip_tool.py myip -6

  # Ping a host
  python ip_tool.py ping google.com
  python ip_tool.py ping 8.8.8.8 -c 10  # 10 pings

  # Check if ports are open
  python ip_tool.py port example.com 80 443
  # Output: 80   open    http
  #         443  open    https

  python ip_tool.py port localhost 22 3306 5432 6379
  # Scan common service ports

  # Resolve hostname to IP
  python ip_tool.py resolve google.com
  # Output: 142.250.x.x

  python ip_tool.py resolve google.com -a  # all addresses

  # Reverse DNS lookup
  python ip_tool.py reverse 8.8.8.8
  # Output: dns.google

  # CIDR calculator
  python ip_tool.py cidr 192.168.1.0/24
  # Output: Network: 192.168.1.0, Netmask: 255.255.255.0
  #         Broadcast: 192.168.1.255, Usable hosts: 254

  python ip_tool.py cidr 10.0.0.0/8 -l  # list all hosts (if small range)
""",
    )
    subparsers = parser.add_subparsers(dest="command", help="Command")

    # Info
    p = subparsers.add_parser("info", help="IP address info")
    p.add_argument("ip", help="IP address or hostname")
    p.set_defaults(func=cmd_info)

    # Lookup
    p = subparsers.add_parser("lookup", aliases=["geo"], help="IP geolocation")
    p.add_argument("ip", help="IP address")
    p.set_defaults(func=cmd_lookup)

    # My IP
    p = subparsers.add_parser("myip", aliases=["me"], help="Get your public IP")
    p.add_argument("-6", "--v6", action="store_true", help="Get IPv6")
    p.add_argument("-s", "--simple", action="store_true", help="Just print IP")
    p.add_argument("-l", "--lookup", action="store_true", help="Also lookup geolocation")
    p.set_defaults(func=cmd_myip)

    # Ping
    p = subparsers.add_parser("ping", help="Ping a host")
    p.add_argument("host", help="Host to ping")
    p.add_argument("-c", "--count", type=int, default=4, help="Number of pings")
    p.set_defaults(func=cmd_ping)

    # Port
    p = subparsers.add_parser("port", aliases=["scan"], help="Check if port is open")
    p.add_argument("host", help="Host to check")
    p.add_argument("ports", type=int, nargs="+", help="Port(s) to check")
    p.add_argument("-t", "--timeout", type=float, default=2.0, help="Timeout (seconds)")
    p.set_defaults(func=cmd_port)

    # Resolve
    p = subparsers.add_parser("resolve", aliases=["dns"], help="Resolve hostname")
    p.add_argument("hostname", help="Hostname to resolve")
    p.add_argument("-a", "--all", action="store_true", help="Get all addresses")
    p.set_defaults(func=cmd_resolve)

    # Reverse
    p = subparsers.add_parser("reverse", aliases=["rdns"], help="Reverse DNS lookup")
    p.add_argument("ip", help="IP address")
    p.set_defaults(func=cmd_reverse)

    # CIDR
    p = subparsers.add_parser("cidr", help="CIDR calculator")
    p.add_argument("cidr", help="CIDR notation (e.g., 192.168.1.0/24)")
    p.add_argument("-l", "--list-hosts", action="store_true", help="List all hosts")
    p.set_defaults(func=cmd_cidr)

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
