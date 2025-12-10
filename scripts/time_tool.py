#!/usr/bin/env python3
"""Time utilities - conversion, timezone handling, countdown, stopwatch."""

import argparse
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path as PathLib
from zoneinfo import ZoneInfo, available_timezones

# Add parent directory to path to import utils
sys.path.insert(0, str(PathLib(__file__).parent.parent))

from utils import Datetime, Terminal


def cmd_now(args: argparse.Namespace) -> int:
    """Show current time."""
    if args.timezone:
        try:
            tz = ZoneInfo(args.timezone)
        except KeyError:
            print(Terminal.colorize(f"Unknown timezone: {args.timezone}", color="red"))
            return 1
    else:
        tz = None

    now = datetime.now(tz or timezone.utc)

    if args.format:
        print(now.strftime(args.format))
    else:
        print(f"\n{Terminal.colorize('Current Time', color='cyan', bold=True)}")
        Terminal.print_line("─", width=40)
        print(f"Local:     {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"UTC:       {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"ISO:       {datetime.now(timezone.utc).isoformat()}")
        print(f"Unix:      {int(time.time())}")
        print(f"Unix (ms): {int(time.time() * 1000)}")

    return 0


def cmd_convert(args: argparse.Namespace) -> int:
    """Convert between time formats."""
    # Parse input
    if args.input.isdigit():
        # Unix timestamp
        ts = int(args.input)
        if ts > 10000000000:  # Likely milliseconds
            ts = ts / 1000
        dt = datetime.fromtimestamp(ts, tz=timezone.utc)
    else:
        dt = Datetime.parse(args.input)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)

    # Apply timezone if specified
    if args.to_tz:
        try:
            tz = ZoneInfo(args.to_tz)
            dt = dt.astimezone(tz)
        except KeyError:
            print(Terminal.colorize(f"Unknown timezone: {args.to_tz}", color="red"))
            return 1

    # Output
    if args.format:
        print(dt.strftime(args.format))
    elif args.unix:
        print(int(dt.timestamp()))
    elif args.iso:
        print(dt.isoformat())
    else:
        print(f"\n{Terminal.colorize('Converted Time', color='cyan', bold=True)}")
        Terminal.print_line("─", width=40)
        print(f"Input:     {args.input}")
        print(f"Datetime:  {dt.strftime('%Y-%m-%d %H:%M:%S %Z')}")
        print(f"ISO:       {dt.isoformat()}")
        print(f"Unix:      {int(dt.timestamp())}")
        print(f"Unix (ms): {int(dt.timestamp() * 1000)}")

    return 0


def cmd_diff(args: argparse.Namespace) -> int:
    """Calculate time difference."""
    dt1 = Datetime.parse(args.time1)
    dt2 = Datetime.parse(args.time2)

    diff = abs(dt2 - dt1)

    print(f"\n{Terminal.colorize('Time Difference', color='cyan', bold=True)}")
    Terminal.print_line("─", width=40)
    print(f"From: {dt1}")
    print(f"To:   {dt2}")
    print()

    total_seconds = int(diff.total_seconds())
    days = diff.days
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    print(f"Days:    {days}")
    print(f"Hours:   {hours}")
    print(f"Minutes: {minutes}")
    print(f"Seconds: {seconds}")
    print()
    print(f"Total seconds: {total_seconds}")
    print(f"Total minutes: {total_seconds // 60}")
    print(f"Total hours:   {total_seconds // 3600}")

    return 0


def cmd_add(args: argparse.Namespace) -> int:
    """Add duration to time."""
    if args.time:
        dt = Datetime.parse(args.time)
    else:
        dt = datetime.now()

    # Parse duration
    delta = timedelta()
    if args.days:
        delta += timedelta(days=args.days)
    if args.hours:
        delta += timedelta(hours=args.hours)
    if args.minutes:
        delta += timedelta(minutes=args.minutes)
    if args.seconds:
        delta += timedelta(seconds=args.seconds)
    if args.weeks:
        delta += timedelta(weeks=args.weeks)

    result = dt + delta

    if args.format:
        print(result.strftime(args.format))
    else:
        print(result.isoformat())

    return 0


def cmd_zones(args: argparse.Namespace) -> int:
    """List or search timezones."""
    all_zones = sorted(available_timezones())

    if args.search:
        search = args.search.lower()
        zones = [z for z in all_zones if search in z.lower()]
    else:
        zones = all_zones

    if args.with_offset:
        now = datetime.now(timezone.utc)
        for zone in zones:
            try:
                tz = ZoneInfo(zone)
                offset = now.astimezone(tz).strftime('%z')
                print(f"{offset}  {zone}")
            except Exception:
                print(f"      {zone}")
    else:
        for zone in zones:
            print(zone)

    return 0


def cmd_countdown(args: argparse.Namespace) -> int:
    """Countdown timer."""
    # Parse duration
    total_seconds = 0
    if args.hours:
        total_seconds += args.hours * 3600
    if args.minutes:
        total_seconds += args.minutes * 60
    if args.seconds:
        total_seconds += args.seconds

    if total_seconds <= 0:
        print(Terminal.colorize("Duration must be positive", color="red"))
        return 1

    print(Terminal.colorize("Countdown started. Press Ctrl+C to stop.", color="cyan"))
    print()

    try:
        while total_seconds > 0:
            hours, remainder = divmod(total_seconds, 3600)
            minutes, seconds = divmod(remainder, 60)

            display = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
            print(f"\r{Terminal.colorize(display, color='yellow', bold=True)}", end="")
            sys.stdout.flush()

            time.sleep(1)
            total_seconds -= 1

        print(f"\r{Terminal.colorize('00:00:00', color='green', bold=True)}")
        print(Terminal.colorize("\n⏰ Time's up!", color="green", bold=True))

        if args.message:
            print(f"\n{args.message}")

    except KeyboardInterrupt:
        print(Terminal.colorize("\n\nCountdown cancelled", color="yellow"))

    return 0


def cmd_stopwatch(args: argparse.Namespace) -> int:
    """Stopwatch."""
    print(Terminal.colorize("Stopwatch started. Press Ctrl+C to stop.", color="cyan"))
    print()

    start = time.time()
    laps = []

    try:
        while True:
            elapsed = time.time() - start
            hours, remainder = divmod(int(elapsed), 3600)
            minutes, seconds = divmod(remainder, 60)
            millis = int((elapsed % 1) * 100)

            display = f"{hours:02d}:{minutes:02d}:{seconds:02d}.{millis:02d}"
            print(f"\r{Terminal.colorize(display, color='yellow', bold=True)}", end="")
            sys.stdout.flush()

            time.sleep(0.01)

    except KeyboardInterrupt:
        elapsed = time.time() - start
        hours, remainder = divmod(int(elapsed), 3600)
        minutes, seconds = divmod(remainder, 60)
        millis = int((elapsed % 1) * 1000)

        print(f"\r{Terminal.colorize(f'{hours:02d}:{minutes:02d}:{seconds:02d}.{millis:03d}', color='green', bold=True)}")
        print(Terminal.colorize(f"\nTotal: {elapsed:.3f} seconds", color="green"))

    return 0


def cmd_epoch(args: argparse.Namespace) -> int:
    """Convert to/from epoch."""
    if args.value:
        # Convert from epoch
        ts = int(args.value)
        if ts > 10000000000:
            ts = ts / 1000

        dt = datetime.fromtimestamp(ts, tz=timezone.utc)
        print(dt.isoformat())
    else:
        # Show current epoch
        now = time.time()
        print(f"Epoch (seconds):      {int(now)}")
        print(f"Epoch (milliseconds): {int(now * 1000)}")

    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Time utilities - conversion, timezone, countdown, stopwatch.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Show current time in various formats
  python time_tool.py now
  # Output: Local: 2024-01-15 10:30:45, UTC: ..., Unix: 1705315845

  # Custom format
  python time_tool.py now -f "%%Y-%%m-%%d"

  # Time in specific timezone
  python time_tool.py now -z "America/New_York"

  # Convert between formats
  python time_tool.py convert 1705315845
  # Output: 2024-01-15T10:30:45+00:00 (from Unix timestamp)

  python time_tool.py convert "2024-01-15 10:30:45" --unix
  # Output: 1705315845

  python time_tool.py convert 1705315845 -z "Asia/Tokyo"
  # Convert and show in Tokyo timezone

  # Calculate time difference
  python time_tool.py diff "2024-01-01" "2024-12-31"
  # Output: Days: 365, Hours: 8760, Total seconds: 31536000

  # Add duration to time
  python time_tool.py add -d 7 -H 3
  # Output: (7 days, 3 hours from now)

  python time_tool.py add "2024-01-15" -d 30
  # Output: 2024-02-14 (30 days from given date)

  # List timezones
  python time_tool.py zones
  python time_tool.py zones america  # search for "america"
  python time_tool.py zones -o       # with UTC offsets

  # Countdown timer
  python time_tool.py countdown -m 5             # 5 minutes
  python time_tool.py countdown -H 1 -m 30       # 1 hour 30 minutes
  python time_tool.py countdown -s 30 --message "Break time!"

  # Stopwatch
  python time_tool.py stopwatch
  # Press Ctrl+C to stop

  # Epoch conversion
  python time_tool.py epoch
  # Output: Epoch (seconds): 1705315845, Epoch (ms): 1705315845123

  python time_tool.py epoch 1705315845
  # Output: 2024-01-15T10:30:45+00:00
""",
    )
    subparsers = parser.add_subparsers(dest="command", help="Command")

    # Now
    p = subparsers.add_parser("now", help="Show current time")
    p.add_argument("-z", "--timezone", help="Timezone")
    p.add_argument("-f", "--format", help="strftime format")
    p.set_defaults(func=cmd_now)

    # Convert
    p = subparsers.add_parser("convert", aliases=["conv"], help="Convert time format")
    p.add_argument("input", help="Time to convert")
    p.add_argument("-z", "--to-tz", help="Target timezone")
    p.add_argument("-f", "--format", help="Output format")
    p.add_argument("--unix", action="store_true", help="Output as Unix timestamp")
    p.add_argument("--iso", action="store_true", help="Output as ISO format")
    p.set_defaults(func=cmd_convert)

    # Diff
    p = subparsers.add_parser("diff", help="Calculate time difference")
    p.add_argument("time1", help="First time")
    p.add_argument("time2", help="Second time")
    p.set_defaults(func=cmd_diff)

    # Add
    p = subparsers.add_parser("add", help="Add duration to time")
    p.add_argument("time", nargs="?", help="Start time (default: now)")
    p.add_argument("-d", "--days", type=int, default=0)
    p.add_argument("-H", "--hours", type=int, default=0)
    p.add_argument("-m", "--minutes", type=int, default=0)
    p.add_argument("-s", "--seconds", type=int, default=0)
    p.add_argument("-w", "--weeks", type=int, default=0)
    p.add_argument("-f", "--format", help="Output format")
    p.set_defaults(func=cmd_add)

    # Zones
    p = subparsers.add_parser("zones", aliases=["tz"], help="List timezones")
    p.add_argument("search", nargs="?", help="Search filter")
    p.add_argument("-o", "--with-offset", action="store_true", help="Show UTC offsets")
    p.set_defaults(func=cmd_zones)

    # Countdown
    p = subparsers.add_parser("countdown", aliases=["timer"], help="Countdown timer")
    p.add_argument("-H", "--hours", type=int, default=0)
    p.add_argument("-m", "--minutes", type=int, default=0)
    p.add_argument("-s", "--seconds", type=int, default=0)
    p.add_argument("--message", help="Message when done")
    p.set_defaults(func=cmd_countdown)

    # Stopwatch
    p = subparsers.add_parser("stopwatch", aliases=["sw"], help="Stopwatch")
    p.set_defaults(func=cmd_stopwatch)

    # Epoch
    p = subparsers.add_parser("epoch", help="Epoch conversion")
    p.add_argument("value", nargs="?", help="Epoch to convert")
    p.set_defaults(func=cmd_epoch)

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
