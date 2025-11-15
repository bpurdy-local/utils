"""Comprehensive tests for miscellaneous utilities."""

from utils import (
    bytes_to_human,
    clamp,
    generate_id,
    hash_string,
    memoize,
    once,
    percentage,
)


class TestGenerateId:
    """Test generate_id function."""

    def test_generate_id_basic(self):
        """Test basic ID generation."""
        result = generate_id(10)
        assert len(result) == 10
        assert isinstance(result, str)

    def test_generate_id_different_lengths(self):
        """Test ID generation with different lengths."""
        assert len(generate_id(5)) == 5
        assert len(generate_id(20)) == 20

    def test_generate_id_custom_chars(self):
        """Test ID generation with custom characters."""
        result = generate_id(10, chars="01")
        assert len(result) == 10
        assert all(c in "01" for c in result)

    def test_generate_id_alphanumeric(self):
        """Test ID generation uses alphanumeric by default."""
        result = generate_id(100)
        assert all(c.isalnum() for c in result)

    def test_generate_id_uniqueness(self):
        """Test that generated IDs are likely unique."""
        ids = [generate_id(20) for _ in range(100)]
        assert len(set(ids)) == 100  # All should be unique


class TestHashString:
    """Test hash_string function."""

    def test_hash_string_sha256(self):
        """Test SHA256 hashing."""
        result = hash_string("hello")
        assert len(result) == 64  # SHA256 produces 64 hex chars
        assert isinstance(result, str)
        assert all(c in "0123456789abcdef" for c in result)

    def test_hash_string_sha256_consistent(self):
        """Test SHA256 produces consistent results."""
        result1 = hash_string("hello")
        result2 = hash_string("hello")
        assert result1 == result2

    def test_hash_string_sha256_different(self):
        """Test SHA256 produces different results for different inputs."""
        result1 = hash_string("hello")
        result2 = hash_string("world")
        assert result1 != result2

    def test_hash_string_md5(self):
        """Test MD5 hashing."""
        result = hash_string("hello", algorithm="md5")
        assert len(result) == 32  # MD5 produces 32 hex chars

    def test_hash_string_sha1(self):
        """Test SHA1 hashing."""
        result = hash_string("hello", algorithm="sha1")
        assert len(result) == 40  # SHA1 produces 40 hex chars

    def test_hash_string_sha512(self):
        """Test SHA512 hashing."""
        result = hash_string("hello", algorithm="sha512")
        assert len(result) == 128  # SHA512 produces 128 hex chars

    def test_hash_string_empty(self):
        """Test hashing empty string."""
        result = hash_string("")
        assert isinstance(result, str)
        assert len(result) > 0


class TestClamp:
    """Test clamp function."""

    def test_clamp_basic(self):
        """Test basic clamping."""
        assert clamp(15, 0, 10) == 10
        assert clamp(-5, 0, 10) == 0
        assert clamp(5, 0, 10) == 5

    def test_clamp_at_min(self):
        """Test clamping at minimum."""
        assert clamp(0, 0, 10) == 0
        assert clamp(-1, 0, 10) == 0

    def test_clamp_at_max(self):
        """Test clamping at maximum."""
        assert clamp(10, 0, 10) == 10
        assert clamp(11, 0, 10) == 10

    def test_clamp_negative_range(self):
        """Test clamping with negative range."""
        assert clamp(-15, -10, -5) == -10
        assert clamp(-3, -10, -5) == -5


class TestMemoize:
    """Test memoize decorator."""

    def test_memoize_caches_results(self):
        """Test that memoize caches function results."""
        call_count = 0

        @memoize
        def test_func(x):
            nonlocal call_count
            call_count += 1
            return x * 2

        result1 = test_func(5)
        result2 = test_func(5)  # Should use cache

        assert result1 == 10
        assert result2 == 10
        assert call_count == 1  # Function should only be called once

    def test_memoize_different_args(self):
        """Test memoize with different arguments."""
        call_count = 0

        @memoize
        def test_func(x):
            nonlocal call_count
            call_count += 1
            return x * 2

        test_func(5)
        test_func(10)  # Different arg, should call again

        assert call_count == 2

    def test_memoize_with_kwargs(self):
        """Test memoize with keyword arguments."""
        call_count = 0

        @memoize
        def test_func(x, y=0):
            nonlocal call_count
            call_count += 1
            return x + y

        test_func(5, y=10)
        test_func(5, y=10)  # Same args, should use cache

        assert call_count == 1


class TestOnce:
    """Test once decorator."""

    def test_once_executes_only_once(self):
        """Test that once executes function only once."""
        call_count = 0

        @once
        def test_func():
            nonlocal call_count
            call_count += 1
            return call_count

        result1 = test_func()
        result2 = test_func()  # Should return cached result

        assert result1 == 1
        assert result2 == 1
        assert call_count == 1

    def test_once_returns_same_result(self):
        """Test that once returns same result on subsequent calls."""

        @once
        def test_func():
            return "result"

        assert test_func() == "result"
        assert test_func() == "result"
        assert test_func() == "result"


class TestBytesToHuman:
    """Test bytes_to_human function."""

    def test_bytes_to_human_bytes(self):
        """Test bytes conversion."""
        result = bytes_to_human(512)
        assert "B" in result
        assert "512" in result or "0.5" in result

    def test_bytes_to_human_kb(self):
        """Test kilobytes conversion."""
        result = bytes_to_human(1024)
        assert "KB" in result
        assert "1.0" in result

    def test_bytes_to_human_mb(self):
        """Test megabytes conversion."""
        result = bytes_to_human(1048576)
        assert "MB" in result
        assert "1.0" in result

    def test_bytes_to_human_gb(self):
        """Test gigabytes conversion."""
        result = bytes_to_human(1073741824)
        assert "GB" in result
        assert "1.0" in result

    def test_bytes_to_human_zero(self):
        """Test bytes conversion with zero."""
        result = bytes_to_human(0)
        assert "B" in result

    def test_bytes_to_human_large(self):
        """Test bytes conversion with large number."""
        result = bytes_to_human(1099511627776)  # 1 TB
        assert "TB" in result


class TestPercentage:
    """Test percentage function."""

    def test_percentage_basic(self):
        """Test basic percentage calculation."""
        assert percentage(25, 100) == 25.0
        assert percentage(50, 100) == 50.0

    def test_percentage_decimal(self):
        """Test percentage with decimals."""
        result = percentage(1, 3, decimals=2)
        assert result == 33.33

    def test_percentage_zero_total(self):
        """Test percentage with zero total."""
        assert percentage(10, 0) == 0.0

    def test_percentage_zero_value(self):
        """Test percentage with zero value."""
        assert percentage(0, 100) == 0.0

    def test_percentage_over_100(self):
        """Test percentage over 100."""
        assert percentage(150, 100) == 150.0

    def test_percentage_custom_decimals(self):
        """Test percentage with custom decimal places."""
        result = percentage(1, 3, decimals=4)
        assert result == 33.3333
