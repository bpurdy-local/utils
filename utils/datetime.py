from datetime import datetime, timedelta, tzinfo

try:
    import arrow  # type: ignore[import-untyped]

    HAS_ARROW = True
except ImportError:
    HAS_ARROW = False
    arrow = None  # type: ignore[assignment]


class Datetime:
    @staticmethod
    def parse(date_str: str, *, format_str: str | None = None) -> datetime:
        if format_str is not None:
            try:
                return datetime.strptime(date_str, format_str)
            except ValueError as e:
                raise ValueError(
                    f"time data {date_str!r} does not match format {format_str!r}"
                ) from e

        if HAS_ARROW and arrow is not None:
            try:
                arrow_dt = arrow.get(date_str)
                return arrow_dt.datetime
            except (ValueError, TypeError, Exception):  # type: ignore[misc]
                pass

        formats = [
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d %H:%M:%S.%f",
            "%Y-%m-%d %H:%M",
            "%Y-%m-%d",
            "%m/%d/%Y %H:%M:%S",
            "%m/%d/%Y %H:%M",
            "%m/%d/%Y",
            "%d/%m/%Y %H:%M:%S",
            "%d/%m/%Y %H:%M",
            "%d/%m/%Y",
            "%Y/%m/%d %H:%M:%S",
            "%Y/%m/%d %H:%M",
            "%Y/%m/%d",
            "%B %d, %Y %H:%M:%S",
            "%B %d, %Y %H:%M",
            "%B %d, %Y",
            "%b %d, %Y %H:%M:%S",
            "%b %d, %Y %H:%M",
            "%b %d, %Y",
            "%d %B %Y %H:%M:%S",
            "%d %B %Y %H:%M",
            "%d %B %Y",
            "%d %b %Y %H:%M:%S",
            "%d %b %Y %H:%M",
            "%d %b %Y",
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%dT%H:%M:%S.%f",
            "%Y-%m-%dT%H:%M:%SZ",
            "%Y-%m-%dT%H:%M:%S.%fZ",
        ]

        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue

        try:
            return datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        except ValueError:
            pass

        try:
            timestamp = float(date_str)
            return datetime.fromtimestamp(timestamp)
        except (ValueError, OSError):
            pass

        raise ValueError(f"Unable to parse date string: {date_str}")

    @staticmethod
    def from_iso(iso_str: str) -> datetime:
        return datetime.fromisoformat(iso_str.replace("Z", "+00:00"))

    @staticmethod
    def from_timestamp(timestamp: float, *, tz: tzinfo | None = None) -> datetime:
        if tz is not None:
            return datetime.fromtimestamp(timestamp, tz=tz)
        return datetime.fromtimestamp(timestamp)

    @staticmethod
    def format(dt: datetime, *, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
        return dt.strftime(format_str)

    @staticmethod
    def to_iso(dt: datetime) -> str:
        return dt.isoformat()

    @staticmethod
    def now(*, tz: tzinfo | None = None) -> datetime:
        if tz is not None:
            return datetime.now(tz)
        return datetime.now()

    @staticmethod
    def human_time(dt: datetime, *, now: datetime | None = None) -> str:
        if now is None:
            now = datetime.now()

        diff = now - dt
        seconds = diff.total_seconds()

        if seconds < 60:
            return "just now"
        elif seconds < 3600:
            minutes = int(seconds / 60)
            return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
        elif seconds < 86400:
            hours = int(seconds / 3600)
            return f"{hours} hour{'s' if hours != 1 else ''} ago"
        elif seconds < 604800:
            days = int(seconds / 86400)
            return f"{days} day{'s' if days != 1 else ''} ago"
        elif seconds < 2592000:
            weeks = int(seconds / 604800)
            return f"{weeks} week{'s' if weeks != 1 else ''} ago"
        elif seconds < 31536000:
            months = int(seconds / 2592000)
            return f"{months} month{'s' if months != 1 else ''} ago"
        else:
            years = int(seconds / 31536000)
            return f"{years} year{'s' if years != 1 else ''} ago"

    @staticmethod
    def start_of_day(dt: datetime) -> datetime:
        return dt.replace(hour=0, minute=0, second=0, microsecond=0)

    @staticmethod
    def end_of_day(dt: datetime) -> datetime:
        return dt.replace(hour=23, minute=59, second=59, microsecond=999999)

    @staticmethod
    def days_between(dt: datetime, *, other: datetime) -> int:
        return (other - dt).days

    @staticmethod
    def is_weekend(dt: datetime) -> bool:
        return dt.weekday() >= 5

    @staticmethod
    def is_weekday(dt: datetime) -> bool:
        return dt.weekday() < 5

    @staticmethod
    def add_days(dt: datetime, *, days: int) -> datetime:
        return dt + timedelta(days=days)

    @staticmethod
    def add_hours(dt: datetime, *, hours: int) -> datetime:
        return dt + timedelta(hours=hours)

    @staticmethod
    def add_minutes(dt: datetime, *, minutes: int) -> datetime:
        return dt + timedelta(minutes=minutes)

    @staticmethod
    def add_weeks(dt: datetime, *, weeks: int) -> datetime:
        return dt + timedelta(weeks=weeks)

    @staticmethod
    def add_months(dt: datetime, *, months: int) -> datetime:
        return dt + timedelta(days=months * 30)

    @staticmethod
    def add_years(dt: datetime, *, years: int) -> datetime:
        return dt.replace(year=dt.year + years)

    @staticmethod
    def start_of_week(dt: datetime, *, week_start: int = 0) -> datetime:
        days_since_start = (dt.weekday() - week_start) % 7
        start = dt - timedelta(days=days_since_start)
        return start.replace(hour=0, minute=0, second=0, microsecond=0)

    @staticmethod
    def end_of_week(dt: datetime, *, week_start: int = 0) -> datetime:
        days_until_end = (6 - (dt.weekday() - week_start) % 7) % 7
        if days_until_end == 0:
            days_until_end = 7
        end = dt + timedelta(days=days_until_end - 1)
        return end.replace(hour=23, minute=59, second=59, microsecond=999999)

    @staticmethod
    def start_of_month(dt: datetime) -> datetime:
        start = dt.replace(day=1)
        return start.replace(hour=0, minute=0, second=0, microsecond=0)

    @staticmethod
    def end_of_month(dt: datetime) -> datetime:
        if dt.month == 12:
            next_month = dt.replace(year=dt.year + 1, month=1, day=1)
        else:
            next_month = dt.replace(month=dt.month + 1, day=1)
        end = next_month - timedelta(days=1)
        return end.replace(hour=23, minute=59, second=59, microsecond=999999)

    @staticmethod
    def start_of_year(dt: datetime) -> datetime:
        start = dt.replace(month=1, day=1)
        return start.replace(hour=0, minute=0, second=0, microsecond=0)

    @staticmethod
    def end_of_year(dt: datetime) -> datetime:
        end = dt.replace(month=12, day=31)
        return end.replace(hour=23, minute=59, second=59, microsecond=999999)

    @staticmethod
    def to_rfc822(dt: datetime) -> str:
        return dt.strftime("%a, %d %b %Y %H:%M:%S %z") or dt.strftime("%a, %d %b %Y %H:%M:%S +0000")

    @staticmethod
    def to_rfc3339(dt: datetime) -> str:
        return dt.isoformat()

    @staticmethod
    def to_date_string(dt: datetime) -> str:
        return dt.strftime("%Y-%m-%d")

    @staticmethod
    def to_time_string(dt: datetime) -> str:
        return dt.strftime("%H:%M:%S")

    @staticmethod
    def to_datetime_string(dt: datetime) -> str:
        return dt.strftime("%Y-%m-%d %H:%M:%S")

    @staticmethod
    def to_timestamp(dt: datetime) -> float:
        return dt.timestamp()

    @staticmethod
    def to_readable(dt: datetime) -> str:
        return dt.strftime("%B %d, %Y at %I:%M %p")
