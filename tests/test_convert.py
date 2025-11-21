
from utils.convert import Convert


class TestConvertToBool:
    def test_native_bool_true(self):
        assert Convert.to_bool(True) is True

    def test_native_bool_false(self):
        assert Convert.to_bool(False) is False

    def test_string_true_variants(self):
        assert Convert.to_bool("true") is True
        assert Convert.to_bool("TRUE") is True
        assert Convert.to_bool("True") is True
        assert Convert.to_bool("yes") is True
        assert Convert.to_bool("YES") is True
        assert Convert.to_bool("y") is True
        assert Convert.to_bool("Y") is True
        assert Convert.to_bool("1") is True
        assert Convert.to_bool("on") is True
        assert Convert.to_bool("ON") is True
        assert Convert.to_bool("t") is True
        assert Convert.to_bool("T") is True
        assert Convert.to_bool("enabled") is True
        assert Convert.to_bool("enable") is True

    def test_string_false_variants(self):
        assert Convert.to_bool("false") is False
        assert Convert.to_bool("FALSE") is False
        assert Convert.to_bool("False") is False
        assert Convert.to_bool("no") is False
        assert Convert.to_bool("NO") is False
        assert Convert.to_bool("n") is False
        assert Convert.to_bool("N") is False
        assert Convert.to_bool("0") is False
        assert Convert.to_bool("off") is False
        assert Convert.to_bool("OFF") is False
        assert Convert.to_bool("f") is False
        assert Convert.to_bool("F") is False
        assert Convert.to_bool("disabled") is False
        assert Convert.to_bool("disable") is False

    def test_string_with_whitespace(self):
        assert Convert.to_bool("  true  ") is True
        assert Convert.to_bool("  false  ") is False

    def test_int_zero(self):
        assert Convert.to_bool(0) is False

    def test_int_nonzero(self):
        assert Convert.to_bool(1) is True
        assert Convert.to_bool(42) is True
        assert Convert.to_bool(-1) is True

    def test_float_zero(self):
        assert Convert.to_bool(0.0) is False

    def test_float_nonzero(self):
        assert Convert.to_bool(1.0) is True
        assert Convert.to_bool(0.1) is True

    def test_none_returns_default(self):
        assert Convert.to_bool(None) is None
        assert Convert.to_bool(None, default=False) is False
        assert Convert.to_bool(None, default=True) is True

    def test_invalid_string_returns_default(self):
        assert Convert.to_bool("invalid") is None
        assert Convert.to_bool("invalid", default=False) is False

    def test_invalid_type_returns_default(self):
        assert Convert.to_bool([1, 2, 3], default=False) is False
        assert Convert.to_bool({"key": "value"}, default=True) is True


class TestConvertToInt:
    def test_native_int(self):
        assert Convert.to_int(123) == 123

    def test_string_int(self):
        assert Convert.to_int("123") == 123

    def test_string_with_commas(self):
        assert Convert.to_int("1,234") == 1234
        assert Convert.to_int("1,234,567") == 1234567

    def test_string_with_decimal(self):
        assert Convert.to_int("123.45") == 123
        assert Convert.to_int("1,234.56") == 1234

    def test_float(self):
        assert Convert.to_int(123.45) == 123
        assert Convert.to_int(123.99) == 123

    def test_bool_true(self):
        assert Convert.to_int(True) == 1

    def test_bool_false(self):
        assert Convert.to_int(False) == 0

    def test_string_with_whitespace(self):
        assert Convert.to_int("  123  ") == 123

    def test_negative_int(self):
        assert Convert.to_int("-123") == -123
        assert Convert.to_int(-123) == -123

    def test_invalid_string_returns_default(self):
        assert Convert.to_int("invalid") is None
        assert Convert.to_int("invalid", default=0) == 0

    def test_none_returns_default(self):
        assert Convert.to_int(None) is None
        assert Convert.to_int(None, default=0) == 0


class TestConvertToFloat:
    def test_native_float(self):
        assert Convert.to_float(123.45) == 123.45

    def test_string_float(self):
        assert Convert.to_float("123.45") == 123.45

    def test_string_with_commas(self):
        assert Convert.to_float("1,234.56") == 1234.56

    def test_int(self):
        assert Convert.to_float(123) == 123.0

    def test_string_int(self):
        assert Convert.to_float("123") == 123.0

    def test_bool_true(self):
        assert Convert.to_float(True) == 1.0

    def test_bool_false(self):
        assert Convert.to_float(False) == 0.0

    def test_string_with_whitespace(self):
        assert Convert.to_float("  123.45  ") == 123.45

    def test_negative_float(self):
        assert Convert.to_float("-123.45") == -123.45
        assert Convert.to_float(-123.45) == -123.45

    def test_invalid_string_returns_default(self):
        assert Convert.to_float("invalid") is None
        assert Convert.to_float("invalid", default=0.0) == 0.0

    def test_none_returns_default(self):
        assert Convert.to_float(None) is None
        assert Convert.to_float(None, default=0.0) == 0.0


class TestConvertToStr:
    def test_int(self):
        assert Convert.to_str(123) == "123"

    def test_float(self):
        assert Convert.to_str(123.45) == "123.45"

    def test_bool(self):
        assert Convert.to_str(True) == "True"
        assert Convert.to_str(False) == "False"

    def test_list(self):
        assert Convert.to_str([1, 2, 3]) == "[1, 2, 3]"

    def test_dict(self):
        result = Convert.to_str({"a": 1})
        assert "a" in result
        assert "1" in result

    def test_none_returns_empty(self):
        assert Convert.to_str(None) == ""

    def test_none_with_default(self):
        assert Convert.to_str(None, default="N/A") == "N/A"

    def test_string(self):
        assert Convert.to_str("hello") == "hello"


class TestConvertToNumber:
    def test_int_stays_int(self):
        result = Convert.to_number("123")
        assert result == 123
        assert isinstance(result, int)

    def test_float_stays_float(self):
        result = Convert.to_number("123.45")
        assert result == 123.45
        assert isinstance(result, float)

    def test_float_whole_number_becomes_int(self):
        result = Convert.to_number("123.0")
        assert result == 123
        assert isinstance(result, int)

    def test_string_with_commas_int(self):
        result = Convert.to_number("1,234")
        assert result == 1234
        assert isinstance(result, int)

    def test_string_with_commas_float(self):
        result = Convert.to_number("1,234.56")
        assert result == 1234.56
        assert isinstance(result, float)

    def test_native_int(self):
        result = Convert.to_number(123)
        assert result == 123
        assert isinstance(result, int)

    def test_native_float(self):
        result = Convert.to_number(123.45)
        assert result == 123.45
        assert isinstance(result, float)

    def test_bool_returns_default(self):
        assert Convert.to_number(True, default=0) == 0
        assert Convert.to_number(False, default=0) == 0

    def test_invalid_returns_default(self):
        assert Convert.to_number("invalid") is None
        assert Convert.to_number("invalid", default=0) == 0


class TestConvertBytesFromHuman:
    def test_bytes(self):
        assert Convert.bytes_from_human("100B") == 100
        assert Convert.bytes_from_human("100") == 100

    def test_kilobytes(self):
        assert Convert.bytes_from_human("1KB") == 1024
        assert Convert.bytes_from_human("2KB") == 2048

    def test_megabytes(self):
        assert Convert.bytes_from_human("1MB") == 1024**2
        assert Convert.bytes_from_human("500MB") == 524288000

    def test_gigabytes(self):
        assert Convert.bytes_from_human("1GB") == 1024**3
        assert Convert.bytes_from_human("1.5GB") == 1610612736

    def test_terabytes(self):
        assert Convert.bytes_from_human("1TB") == 1024**4
        assert Convert.bytes_from_human("2TB") == 2199023255552

    def test_case_insensitive(self):
        assert Convert.bytes_from_human("1kb") == 1024
        assert Convert.bytes_from_human("1Kb") == 1024
        assert Convert.bytes_from_human("1mb") == 1024**2

    def test_with_spaces(self):
        assert Convert.bytes_from_human("1 GB") == 1024**3
        assert Convert.bytes_from_human("2 MB") == 2 * 1024**2

    def test_decimal_values(self):
        assert Convert.bytes_from_human("0.5KB") == 512
        assert Convert.bytes_from_human("1.5MB") == int(1.5 * 1024**2)

    def test_invalid_returns_default(self):
        assert Convert.bytes_from_human("invalid") is None
        assert Convert.bytes_from_human("invalid", default=0) == 0

    def test_non_string_returns_default(self):
        assert Convert.bytes_from_human(123, default=0) == 0


class TestConvertDuration:
    def test_seconds(self):
        assert Convert.duration("30s") == 30
        assert Convert.duration("60s") == 60

    def test_minutes(self):
        assert Convert.duration("1m") == 60
        assert Convert.duration("30m") == 1800

    def test_hours(self):
        assert Convert.duration("1h") == 3600
        assert Convert.duration("2h") == 7200

    def test_days(self):
        assert Convert.duration("1d") == 86400
        assert Convert.duration("2d") == 172800

    def test_combined(self):
        assert Convert.duration("1h 30m") == 5400
        assert Convert.duration("2h 30m 15s") == 9015
        assert Convert.duration("1d 2h 30m 15s") == 95415

    def test_no_spaces(self):
        assert Convert.duration("1h30m") == 5400
        assert Convert.duration("2h30m15s") == 9015

    def test_decimal_values(self):
        assert Convert.duration("1.5h") == 5400
        assert Convert.duration("2.5m") == 150

    def test_case_insensitive(self):
        assert Convert.duration("2H") == 7200
        assert Convert.duration("30M") == 1800
        assert Convert.duration("1D") == 86400

    def test_invalid_returns_default(self):
        assert Convert.duration("invalid") is None
        assert Convert.duration("invalid", default=0) == 0

    def test_non_string_returns_default(self):
        assert Convert.duration(123, default=0) == 0


class TestConvertSafeCast:
    def test_already_correct_type(self):
        assert Convert.safe_cast(123, int) == 123
        assert Convert.safe_cast("hello", str) == "hello"
        assert Convert.safe_cast([1, 2], list) == [1, 2]

    def test_string_to_int(self):
        assert Convert.safe_cast("123", int) == 123

    def test_string_to_float(self):
        assert Convert.safe_cast("123.45", float) == 123.45

    def test_string_to_bool(self):
        assert Convert.safe_cast("true", bool) is True
        assert Convert.safe_cast("false", bool) is False

    def test_int_to_str(self):
        assert Convert.safe_cast(123, str) == "123"

    def test_list_to_tuple(self):
        assert Convert.safe_cast([1, 2, 3], tuple) == (1, 2, 3)

    def test_tuple_to_list(self):
        assert Convert.safe_cast((1, 2, 3), list) == [1, 2, 3]

    def test_invalid_conversion_returns_default(self):
        assert Convert.safe_cast("invalid", int, default=0) == 0
        assert Convert.safe_cast("invalid", float, default=0.0) == 0.0

    def test_none_returns_default(self):
        assert Convert.safe_cast(None, int, default=0) == 0
        assert Convert.safe_cast(None, str, default="N/A") == "N/A"


class TestConvertToList:
    def test_comma_separated_string(self):
        assert Convert.to_list("a,b,c") == ["a", "b", "c"]

    def test_comma_separated_with_spaces(self):
        assert Convert.to_list("a, b, c") == ["a", "b", "c"]

    def test_single_item(self):
        assert Convert.to_list("a") == ["a"]

    def test_native_list(self):
        assert Convert.to_list([1, 2, 3]) == [1, 2, 3]

    def test_tuple_to_list(self):
        assert Convert.to_list((1, 2, 3)) == [1, 2, 3]

    def test_set_to_list(self):
        result = Convert.to_list({1, 2, 3})
        assert isinstance(result, list)
        assert set(result) == {1, 2, 3}

    def test_custom_separator(self):
        assert Convert.to_list("a;b;c", separator=";") == ["a", "b", "c"]
        assert Convert.to_list("a|b|c", separator="|") == ["a", "b", "c"]

    def test_empty_string(self):
        assert Convert.to_list("") == []

    def test_none_returns_default(self):
        assert Convert.to_list(None) == []
        assert Convert.to_list(None, default=["default"]) == ["default"]

    def test_single_value_wrapped(self):
        assert Convert.to_list(123) == [123]
        assert Convert.to_list(True) == [True]

    def test_strips_empty_items(self):
        assert Convert.to_list("a, , b, , c") == ["a", "b", "c"]


class TestConvertToDict:
    def test_native_dict(self):
        d = {"a": 1, "b": 2}
        assert Convert.to_dict(d) == d

    def test_list_of_tuples(self):
        assert Convert.to_dict([("a", 1), ("b", 2)]) == {"a": 1, "b": 2}

    def test_none_returns_default(self):
        assert Convert.to_dict(None) == {}
        assert Convert.to_dict(None, default={"key": "value"}) == {"key": "value"}

    def test_invalid_returns_default(self):
        assert Convert.to_dict("invalid") == {}
        assert Convert.to_dict([1, 2, 3], default={}) == {}


class TestConvertEdgeCases:
    def test_empty_string_conversions(self):
        assert Convert.to_int("") is None
        assert Convert.to_float("") is None
        assert Convert.to_bool("") is None
        assert Convert.to_str("") == ""

    def test_whitespace_only_strings(self):
        assert Convert.to_int("   ") is None
        assert Convert.to_float("   ") is None
        assert Convert.to_bool("   ") is None

    def test_large_numbers(self):
        assert Convert.to_int("999999999999") == 999999999999
        assert Convert.bytes_from_human("999TB") == 999 * 1024**4

    def test_negative_numbers(self):
        assert Convert.to_int("-123") == -123
        assert Convert.to_float("-123.45") == -123.45

    def test_scientific_notation(self):
        assert Convert.to_float("1.5e2") == 150.0
        assert Convert.to_float("1e-3") == 0.001

    def test_unicode_strings(self):
        assert Convert.to_str("Hello 世界") == "Hello 世界"
