"""Comprehensive tests for miscellaneous utilities."""

from utils import Decorators, Integer, Random, String


class TestGenerateId:
    """Test generate_id function."""

    def test_generate_id_basic(self):
        """Test basic ID generation."""
        result = Random.string(length=10)
        assert len(result) == 10
        assert isinstance(result, str)

    def test_generate_id_different_lengths(self):
        """Test ID generation with different lengths."""
        assert len(Random.string(length=5)) == 5
        assert len(Random.string(length=20)) == 20

    def test_generate_id_custom_chars(self):
        """Test ID generation with custom characters."""
        result = Random.string(length=10, chars="01")
        assert len(result) == 10
        assert all(c in "01" for c in result)

    def test_generate_id_alphanumeric(self):
        """Test ID generation uses alphanumeric by default."""
        result = Random.string(length=100)
        assert all(c.isalnum() for c in result)

    def test_generate_id_uniqueness(self):
        """Test that generated IDs are likely unique."""
        ids = [Random.string(length=20) for _ in range(100)]
        assert len(set(ids)) == 100  # All should be unique


class TestHashString:
    """Test hash_string function."""

    def test_hash_string_sha256(self):
        """Test SHA256 hashing."""
        result = String.hash("hello")
        assert len(result) == 64  # SHA256 produces 64 hex chars
        assert isinstance(result, str)
        assert all(c in "0123456789abcdef" for c in result)

    def test_hash_string_sha256_consistent(self):
        """Test SHA256 produces consistent results."""
        result1 = String.hash("hello")
        result2 = String.hash("hello")
        assert result1 == result2

    def test_hash_string_sha256_different(self):
        """Test SHA256 produces different results for different inputs."""
        result1 = String.hash("hello")
        result2 = String.hash("world")
        assert result1 != result2

    def test_hash_string_md5(self):
        """Test MD5 hashing."""
        result = String.hash("hello", algorithm="md5")
        assert len(result) == 32  # MD5 produces 32 hex chars

    def test_hash_string_sha1(self):
        """Test SHA1 hashing."""
        result = String.hash("hello", algorithm="sha1")
        assert len(result) == 40  # SHA1 produces 40 hex chars

    def test_hash_string_sha512(self):
        """Test SHA512 hashing."""
        result = String.hash("hello", algorithm="sha512")
        assert len(result) == 128  # SHA512 produces 128 hex chars

    def test_hash_string_empty(self):
        """Test hashing empty string."""
        result = String.hash("")
        assert isinstance(result, str)
        assert len(result) > 0


class TestClamp:
    """Test clamp function."""

    def test_clamp_basic(self):
        """Test basic clamping."""
        assert Integer.clamp(15, min_val=0, max_val=10) == 10
        assert Integer.clamp(-5, min_val=0, max_val=10) == 0
        assert Integer.clamp(5, min_val=0, max_val=10) == 5

    def test_clamp_at_min(self):
        """Test clamping at minimum."""
        assert Integer.clamp(0, min_val=0, max_val=10) == 0
        assert Integer.clamp(-1, min_val=0, max_val=10) == 0

    def test_clamp_at_max(self):
        """Test clamping at maximum."""
        assert Integer.clamp(10, min_val=0, max_val=10) == 10
        assert Integer.clamp(11, min_val=0, max_val=10) == 10

    def test_clamp_negative_range(self):
        """Test clamping with negative range."""
        assert Integer.clamp(-15, min_val=-10, max_val=-5) == -10
        assert Integer.clamp(-3, min_val=-10, max_val=-5) == -5


class TestMemoize:
    """Test memoize decorator."""

    def test_memoize_caches_results(self):
        """Test that memoize caches function results."""
        call_count = 0

        @Decorators.memoize
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

        @Decorators.memoize
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

        @Decorators.memoize
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

        @Decorators.once
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

        @Decorators.once
        def test_func():
            return "result"

        assert test_func() == "result"
        assert test_func() == "result"
        assert test_func() == "result"


class TestBytesToHuman:
    """Test bytes_to_human function."""

    def test_bytes_to_human_bytes(self):
        """Test bytes conversion."""
        result = Integer.bytes_to_human(512)
        assert "B" in result
        assert "512" in result or "0.5" in result

    def test_bytes_to_human_kb(self):
        """Test kilobytes conversion."""
        result = Integer.bytes_to_human(1024)
        assert "KB" in result
        assert "1.0" in result

    def test_bytes_to_human_mb(self):
        """Test megabytes conversion."""
        result = Integer.bytes_to_human(1048576)
        assert "MB" in result
        assert "1.0" in result

    def test_bytes_to_human_gb(self):
        """Test gigabytes conversion."""
        result = Integer.bytes_to_human(1073741824)
        assert "GB" in result
        assert "1.0" in result

    def test_bytes_to_human_zero(self):
        """Test bytes conversion with zero."""
        result = Integer.bytes_to_human(0)
        assert "B" in result

    def test_bytes_to_human_large(self):
        """Test bytes conversion with large number."""
        result = Integer.bytes_to_human(1099511627776)  # 1 TB
        assert "TB" in result


class TestPercentage:
    """Test percentage function."""

    def test_percentage_basic(self):
        """Test basic percentage calculation."""
        assert Integer.percentage(25, total=100) == 25.0
        assert Integer.percentage(50, total=100) == 50.0

    def test_percentage_decimal(self):
        """Test percentage with decimals."""
        result = Integer.percentage(1, total=3, decimals=2)
        assert result == 33.33

    def test_percentage_zero_total(self):
        """Test percentage with zero total."""
        assert Integer.percentage(10, total=0) == 0.0

    def test_percentage_zero_value(self):
        """Test percentage with zero value."""
        assert Integer.percentage(0, total=100) == 0.0

    def test_percentage_over_100(self):
        """Test percentage over 100."""
        assert Integer.percentage(150, total=100) == 150.0

    def test_percentage_custom_decimals(self):
        """Test percentage with custom decimal places."""
        result = Integer.percentage(1, total=3, decimals=4)
        assert result == 33.3333
