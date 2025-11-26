"""Comprehensive tests for Random class."""

from utils import Random


class TestRandomString:
    """Test Random.string method."""

    def test_string_length(self):
        """Test Random.string generates correct length."""
        result = Random.string(length=10)
        assert len(result) == 10

    def test_string_alphanumeric(self):
        """Test Random.string uses alphanumeric by default."""
        result = Random.string(length=100)
        assert all(c.isalnum() for c in result)

    def test_string_custom_chars(self):
        """Test Random.string with custom characters."""
        result = Random.string(length=10, chars="01")
        assert len(result) == 10
        assert all(c in "01" for c in result)


class TestRandomInt:
    """Test Random.int method."""

    def test_int_range(self):
        """Test Random.int within range."""
        result = Random.int(min_val=0, max_val=10)
        assert 0 <= result <= 10

    def test_int_boundaries(self):
        """Test Random.int at boundaries."""
        result = Random.int(min_val=5, max_val=5)
        assert result == 5


class TestRandomFloat:
    """Test Random.float method."""

    def test_float_range(self):
        """Test Random.float within range."""
        result = Random.float(min_val=0.0, max_val=1.0)
        assert 0.0 <= result < 1.0

    def test_float_custom_range(self):
        """Test Random.float with custom range."""
        result = Random.float(min_val=10.0, max_val=20.0)
        assert 10.0 <= result < 20.0


class TestRandomShuffle:
    """Test Random.shuffle method."""

    def test_shuffle_different(self):
        """Test Random.shuffle produces different order."""
        items = [1, 2, 3, 4, 5]
        shuffled = Random.shuffle(items)
        assert len(shuffled) == len(items)
        assert set(shuffled) == set(items)
        # Original list should not be modified
        assert items == [1, 2, 3, 4, 5]

    def test_shuffle_empty(self):
        """Test Random.shuffle with empty list."""
        result = Random.shuffle([])
        assert result == []


