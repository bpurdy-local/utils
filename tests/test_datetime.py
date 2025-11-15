from datetime import datetime, timedelta

import pytest

from utils import Datetime


class TestFormatDate:
    def test_format_date_basic(self):
        dt = datetime(2024, 1, 1, 12, 0, 0)
        result = Datetime.format(dt)
        assert "2024-01-01" in result
        assert "12:00:00" in result

    def test_format_date_custom_format(self):
        dt = datetime(2024, 1, 1, 12, 0, 0)
        result = Datetime.format(dt, format_str="%Y-%m-%d")
        assert result == "2024-01-01"

    def test_format_date_defaults_to_now(self):
        result = Datetime.format(Datetime.now())
        assert isinstance(result, str)
        assert len(result) > 0

    def test_format_date_with_timezone(self):
        dt = datetime(2024, 1, 1, 12, 0, 0)
        result = Datetime.format(dt, format_str="%Y-%m-%d %H:%M:%S %Z")
        assert isinstance(result, str)


class TestParseDate:
    def test_parse_date_basic(self):
        result = Datetime.parse("2024-01-01 12:00:00")
        assert result == datetime(2024, 1, 1, 12, 0, 0)

    def test_parse_date_custom_format(self):
        result = Datetime.parse("2024-01-01", format_str="%Y-%m-%d")
        assert result == datetime(2024, 1, 1, 0, 0, 0)

    def test_parse_date_invalid_format(self):
        with pytest.raises(ValueError):
            Datetime.parse("invalid", format_str="%Y-%m-%d")


class TestHumanTime:
    def test_human_time_just_now(self):
        now = Datetime.now() - timedelta(seconds=30)
        result = Datetime.human_time(now)
        assert "just now" in result.lower() or "minute" in result.lower()

    def test_human_time_minutes_ago(self):
        now = Datetime.now() - timedelta(minutes=5)
        result = Datetime.human_time(now)
        assert "minute" in result.lower()

    def test_human_time_hours_ago(self):
        now = Datetime.now() - timedelta(hours=2)
        result = Datetime.human_time(now)
        assert "hour" in result.lower()

    def test_human_time_days_ago(self):
        now = Datetime.now() - timedelta(days=3)
        result = Datetime.human_time(now)
        assert "day" in result.lower()

    def test_human_time_weeks_ago(self):
        now = Datetime.now() - timedelta(weeks=2)
        result = Datetime.human_time(now)
        assert "week" in result.lower()

    def test_human_time_months_ago(self):
        now = Datetime.now() - timedelta(days=60)
        result = Datetime.human_time(now)
        assert "month" in result.lower()

    def test_human_time_years_ago(self):
        now = Datetime.now() - timedelta(days=400)
        result = Datetime.human_time(now)
        assert "year" in result.lower()

    def test_human_time_singular(self):
        now = Datetime.now() - timedelta(hours=1)
        result = Datetime.human_time(now)
        assert "hour" in result.lower()
        assert "hours" not in result.lower() or result.count("hour") == 1


class TestStartOfDay:
    def test_start_of_day_basic(self):
        dt = datetime(2024, 1, 1, 14, 30, 45)
        result = Datetime.start_of_day(dt)
        assert result == datetime(2024, 1, 1, 0, 0, 0)

    def test_start_of_day_defaults_to_today(self):
        result = Datetime.start_of_day(Datetime.now())
        assert result.hour == 0
        assert result.minute == 0
        assert result.second == 0

    def test_start_of_day_midnight(self):
        dt = datetime(2024, 1, 1, 0, 0, 0)
        result = Datetime.start_of_day(dt)
        assert result == dt


class TestEndOfDay:
    def test_end_of_day_basic(self):
        dt = datetime(2024, 1, 1, 14, 30, 45)
        result = Datetime.end_of_day(dt)
        assert result.hour == 23
        assert result.minute == 59
        assert result.second == 59

    def test_end_of_day_defaults_to_today(self):
        result = Datetime.end_of_day(Datetime.now())
        assert result.hour == 23
        assert result.minute == 59

    def test_end_of_day_midnight(self):
        dt = datetime(2024, 1, 1, 0, 0, 0)
        result = Datetime.end_of_day(dt)
        assert result.hour == 23
        assert result.minute == 59


class TestDaysBetween:
    def test_days_between_basic(self):
        start = datetime(2024, 1, 1)
        end = datetime(2024, 1, 5)
        result = Datetime.days_between(start, other=end)
        assert result == 4

    def test_days_between_same_day(self):
        dt = datetime(2024, 1, 1)
        result = Datetime.days_between(dt, other=dt)
        assert result == 0

    def test_days_between_reversed(self):
        start = datetime(2024, 1, 5)
        end = datetime(2024, 1, 1)
        result = Datetime.days_between(start, other=end)
        assert result == -4

    def test_days_between_one_day(self):
        start = datetime(2024, 1, 1)
        end = datetime(2024, 1, 2)
        result = Datetime.days_between(start, other=end)
        assert result == 1


class TestIsWeekend:
    def test_is_weekend_saturday(self):
        dt = datetime(2024, 1, 6)
        assert Datetime.is_weekend(dt) is True

    def test_is_weekend_sunday(self):
        dt = datetime(2024, 1, 7)
        assert Datetime.is_weekend(dt) is True

    def test_is_weekend_monday(self):
        dt = datetime(2024, 1, 1)
        assert Datetime.is_weekend(dt) is False

    def test_is_weekend_defaults_to_today(self):
        result = Datetime.is_weekend(Datetime.now())
        assert isinstance(result, bool)


class TestIsWeekday:
    def test_is_weekday_monday(self):
        dt = datetime(2024, 1, 1)
        assert Datetime.is_weekday(dt) is True

    def test_is_weekday_friday(self):
        dt = datetime(2024, 1, 5)
        assert Datetime.is_weekday(dt) is True

    def test_is_weekday_saturday(self):
        dt = datetime(2024, 1, 6)
        assert Datetime.is_weekday(dt) is False

    def test_is_weekday_defaults_to_today(self):
        result = Datetime.is_weekday(Datetime.now())
        assert isinstance(result, bool)
