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


class TestRandomSample:
    """Test Random.sample method."""

    def test_sample_size(self):
        """Test Random.sample returns correct size."""
        items = [1, 2, 3, 4, 5]
        result = Random.sample(items, k=3)
        assert len(result) == 3
        assert all(item in items for item in result)

    def test_sample_all_items(self):
        """Test Random.sample with k equal to list length."""
        items = [1, 2, 3]
        result = Random.sample(items, k=3)
        assert len(result) == 3
        assert set(result) == set(items)


class TestRandomChoice:
    """Test Random.choice method."""

    def test_choice_in_list(self):
        """Test Random.choice returns item from list."""
        items = [1, 2, 3]
        result = Random.choice(items)
        assert result in items

    def test_choice_single_item(self):
        """Test Random.choice with single item."""
        result = Random.choice([42])
        assert result == 42


class TestRandomUUID:
    """Test Random UUID methods."""

    def test_uuid4_format(self):
        """Test Random.uuid4 format."""
        result = Random.uuid4()
        assert len(result) == 36
        assert result.count("-") == 4

    def test_uuid1_format(self):
        """Test Random.uuid1 format."""
        result = Random.uuid1()
        assert len(result) == 36
        assert result.count("-") == 4

    def test_uuid_string(self):
        """Test Random.uuid_string."""
        result = Random.uuid_string()
        assert len(result) == 36
        assert result.count("-") == 4

    def test_uuid_uniqueness(self):
        """Test UUIDs are unique."""
        uuid1 = Random.uuid4()
        uuid2 = Random.uuid4()
        assert uuid1 != uuid2
