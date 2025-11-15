"""Comprehensive tests for common utilities."""

import time

import pytest

from utils import chunk, debounce, flatten, group_by, retry, slugify, throttle


class TestChunk:
    """Test chunk function."""

    def test_chunk_basic(self):
        """Test basic chunking."""
        result = chunk([1, 2, 3, 4, 5], 2)
        assert result == [[1, 2], [3, 4], [5]]

    def test_chunk_exact_size(self):
        """Test chunking with exact size."""
        result = chunk([1, 2, 3, 4], 2)
        assert result == [[1, 2], [3, 4]]

    def test_chunk_single_item(self):
        """Test chunking with single item chunks."""
        result = chunk([1, 2, 3], 1)
        assert result == [[1], [2], [3]]

    def test_chunk_larger_than_list(self):
        """Test chunking with size larger than list."""
        result = chunk([1, 2, 3], 10)
        assert result == [[1, 2, 3]]

    def test_chunk_empty_list(self):
        """Test chunking empty list."""
        result = chunk([], 2)
        assert result == []

    def test_chunk_string(self):
        """Test chunking string."""
        result = chunk("abcdef", 2)
        assert result == [["a", "b"], ["c", "d"], ["e", "f"]]

    def test_chunk_tuple(self):
        """Test chunking tuple."""
        result = chunk((1, 2, 3, 4), 2)
        assert result == [[1, 2], [3, 4]]


class TestFlatten:
    """Test flatten function."""

    def test_flatten_basic(self):
        """Test basic flattening."""
        result = flatten([[1, 2], [3, 4]])
        assert result == [1, 2, 3, 4]

    def test_flatten_nested(self):
        """Test flattening nested lists."""
        result = flatten([[1, 2], [3, 4], [5]])
        assert result == [1, 2, 3, 4, 5]

    def test_flatten_empty(self):
        """Test flattening empty list."""
        result = flatten([])
        assert result == []

    def test_flatten_with_empty_sublists(self):
        """Test flattening with empty sublists."""
        result = flatten([[1, 2], [], [3, 4]])
        assert result == [1, 2, 3, 4]

    def test_flatten_tuples(self):
        """Test flattening tuples."""
        result = flatten([(1, 2), (3, 4)])
        assert result == [1, 2, 3, 4]


class TestGroupBy:
    """Test group_by function."""

    def test_group_by_basic(self):
        """Test basic grouping."""
        result = group_by([1, 2, 3, 4], lambda x: x % 2)
        assert result == {0: [2, 4], 1: [1, 3]}

    def test_group_by_string_key(self):
        """Test grouping by string key."""
        items = [{"type": "a", "val": 1}, {"type": "b", "val": 2}, {"type": "a", "val": 3}]
        result = group_by(items, lambda x: x["type"])
        assert len(result["a"]) == 2
        assert len(result["b"]) == 1

    def test_group_by_empty(self):
        """Test grouping empty list."""
        result = group_by([], lambda x: x)
        assert result == {}

    def test_group_by_single_group(self):
        """Test grouping with single group."""
        result = group_by([1, 2, 3], lambda x: "same")
        assert result == {"same": [1, 2, 3]}


class TestSlugify:
    """Test slugify function."""

    def test_slugify_basic(self):
        """Test basic slugification."""
        assert slugify("Hello World!") == "hello-world"

    def test_slugify_special_chars(self):
        """Test slugification with special characters."""
        assert slugify("Hello@World#Python!") == "helloworldpython"

    def test_slugify_multiple_spaces(self):
        """Test slugification with multiple spaces."""
        assert slugify("Hello    World") == "hello-world"

    def test_slugify_leading_trailing_dashes(self):
        """Test slugification removes leading/trailing dashes."""
        assert slugify("  Hello World  ") == "hello-world"

    def test_slugify_empty(self):
        """Test slugification of empty string."""
        assert slugify("") == ""

    def test_slugify_numbers(self):
        """Test slugification with numbers."""
        assert slugify("Hello 123 World") == "hello-123-world"


class TestDebounce:
    """Test debounce decorator."""

    def test_debounce_delays_execution(self):
        """Test that debounce delays execution."""
        call_count = 0

        @debounce(delay=0.1)
        def test_func():
            nonlocal call_count
            call_count += 1

        test_func()
        assert call_count == 0  # Should not execute immediately

        time.sleep(0.15)
        assert call_count == 1  # Should execute after delay

    def test_debounce_cancels_previous(self):
        """Test that debounce cancels previous calls."""
        call_count = 0

        @debounce(delay=0.1)
        def test_func():
            nonlocal call_count
            call_count += 1

        test_func()
        test_func()  # This should cancel the previous call
        time.sleep(0.15)
        assert call_count == 1  # Should only execute once


class TestThrottle:
    """Test throttle decorator."""

    def test_throttle_limits_execution(self):
        """Test that throttle limits execution frequency."""
        call_count = 0

        @throttle(delay=0.1)
        def test_func():
            nonlocal call_count
            call_count += 1
            return call_count

        result1 = test_func()
        assert result1 == 1

        result2 = test_func()  # Should return None (throttled)
        assert result2 is None
        assert call_count == 1

        time.sleep(0.15)
        result3 = test_func()  # Should execute now
        assert result3 == 2
        assert call_count == 2


class TestRetry:
    """Test retry decorator."""

    def test_retry_succeeds_first_try(self):
        """Test retry when function succeeds on first try."""
        call_count = 0

        @retry(max_attempts=3)
        def test_func():
            nonlocal call_count
            call_count += 1
            return "success"

        result = test_func()
        assert result == "success"
        assert call_count == 1

    def test_retry_succeeds_after_failures(self):
        """Test retry when function succeeds after failures."""
        call_count = 0

        @retry(max_attempts=3, delay=0.01)
        def test_func():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise ValueError("Fail")
            return "success"

        result = test_func()
        assert result == "success"
        assert call_count == 2

    def test_retry_exhausts_attempts(self):
        """Test retry when all attempts fail."""
        call_count = 0

        @retry(max_attempts=3, delay=0.01)
        def test_func():
            nonlocal call_count
            call_count += 1
            raise ValueError("Always fail")

        with pytest.raises(ValueError, match="Always fail"):
            test_func()
        assert call_count == 3

    def test_retry_specific_exceptions(self):
        """Test retry with specific exceptions."""
        call_count = 0

        @retry(max_attempts=2, delay=0.01, exceptions=(ValueError,))
        def test_func():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise ValueError("Fail")
            raise TypeError("Different error")

        with pytest.raises(TypeError, match="Different error"):
            test_func()
        assert call_count == 2

    def test_retry_with_backoff(self):
        """Test retry with exponential backoff."""
        call_times = []

        @retry(max_attempts=3, delay=0.05, backoff=2.0)
        def test_func():
            call_times.append(time.time())
            raise ValueError("Fail")

        start_time = time.time()
        with pytest.raises(ValueError):
            test_func()
        end_time = time.time()

        # Should have delays: 0.05, 0.10 (0.05 * 2)
        # Total time should be at least 0.15 seconds
        assert end_time - start_time >= 0.14
        assert len(call_times) == 3
