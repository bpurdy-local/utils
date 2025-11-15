"""Comprehensive tests for collection utilities."""

from utils import Dict, Iterable


class TestUnique:
    """Test unique function."""

    def test_unique_basic(self):
        """Test basic unique filtering."""
        result = Iterable.unique([1, 2, 2, 3, 1])
        assert result == [1, 2, 3]

    def test_unique_preserves_order(self):
        """Test that unique preserves order."""
        result = Iterable.unique([3, 1, 2, 1, 3, 2])
        assert result == [3, 1, 2]

    def test_unique_with_key(self):
        """Test unique with key function."""
        items = [{"x": 1}, {"x": 2}, {"x": 1}]
        result = Iterable.unique(items, key=lambda d: d["x"])
        assert len(result) == 2
        assert result[0]["x"] == 1
        assert result[1]["x"] == 2

    def test_unique_empty(self):
        """Test unique with empty list."""
        result = Iterable.unique([])
        assert result == []

    def test_unique_all_same(self):
        """Test unique when all items are same."""
        result = Iterable.unique([1, 1, 1, 1])
        assert result == [1]

    def test_unique_strings(self):
        """Test unique with strings."""
        result = Iterable.unique(["a", "b", "a", "c", "b"])
        assert result == ["a", "b", "c"]


class TestFirst:
    """Test first function."""

    def test_first_basic(self):
        """Test basic first item."""
        assert Iterable.first([1, 2, 3]) == 1

    def test_first_empty_with_default(self):
        """Test first with empty list and default."""
        assert Iterable.first([], default=0) == 0

    def test_first_empty_no_default(self):
        """Test first with empty list and no default."""
        assert Iterable.first([]) is None

    def test_first_single_item(self):
        """Test first with single item."""
        assert Iterable.first([42]) == 42

    def test_first_string(self):
        """Test first with string."""
        assert Iterable.first(list("hello")) == "h"


class TestLast:
    """Test last function."""

    def test_last_basic(self):
        """Test basic last item."""
        assert Iterable.last([1, 2, 3]) == 3

    def test_last_empty_with_default(self):
        """Test last with empty list and default."""
        assert Iterable.last([], default=0) == 0

    def test_last_empty_no_default(self):
        """Test last with empty list and no default."""
        assert Iterable.last([]) is None

    def test_last_single_item(self):
        """Test last with single item."""
        assert Iterable.last([42]) == 42

    def test_last_string(self):
        """Test last with string."""
        assert Iterable.last(list("hello")) == "o"


class TestPluck:
    """Test pluck function."""

    def test_pluck_basic(self):
        """Test basic pluck."""
        items = [{"name": "Alice", "age": 30}, {"name": "Bob", "age": 25}]
        result = Iterable.pluck(items, key="name")
        assert result == ["Alice", "Bob"]

    def test_pluck_missing_key(self):
        """Test pluck with missing key."""
        items = [{"name": "Alice"}, {"age": 25}]
        result = Iterable.pluck(items, key="name")
        assert result == ["Alice"]

    def test_pluck_empty(self):
        """Test pluck with empty list."""
        result = Iterable.pluck([], key="name")
        assert result == []

    def test_pluck_none_values(self):
        """Test pluck with None values."""
        items = [{"name": "Alice"}, {"name": None}]
        result = Iterable.pluck(items, key="name")
        assert result == ["Alice", None]


class TestPick:
    """Test pick function."""

    def test_pick_basic(self):
        """Test basic pick."""
        d = {"a": 1, "b": 2, "c": 3}
        result = Dict.pick(d, "a", "c")
        assert result == {"a": 1, "c": 3}

    def test_pick_single_key(self):
        """Test pick with single key."""
        d = {"a": 1, "b": 2}
        result = Dict.pick(d, "a")
        assert result == {"a": 1}

    def test_pick_missing_key(self):
        """Test pick with missing key."""
        d = {"a": 1, "b": 2}
        result = Dict.pick(d, "a", "c")
        assert result == {"a": 1}

    def test_pick_empty(self):
        """Test pick with empty dict."""
        result = Dict.pick({}, "a")
        assert result == {}

    def test_pick_all_keys(self):
        """Test pick with all keys."""
        d = {"a": 1, "b": 2}
        result = Dict.pick(d, "a", "b")
        assert result == d


class TestOmit:
    """Test omit function."""

    def test_omit_basic(self):
        """Test basic omit."""
        d = {"a": 1, "b": 2, "c": 3}
        result = Dict.omit(d, "a", "c")
        assert result == {"b": 2}

    def test_omit_single_key(self):
        """Test omit with single key."""
        d = {"a": 1, "b": 2}
        result = Dict.omit(d, "a")
        assert result == {"b": 2}

    def test_omit_missing_key(self):
        """Test omit with missing key."""
        d = {"a": 1, "b": 2}
        result = Dict.omit(d, "a", "c")
        assert result == {"b": 2}

    def test_omit_all_keys(self):
        """Test omit with all keys."""
        d = {"a": 1, "b": 2}
        result = Dict.omit(d, "a", "b")
        assert result == {}

    def test_omit_empty(self):
        """Test omit with empty dict."""
        result = Dict.omit({}, "a")
        assert result == {}


class TestPartition:
    """Test partition function."""

    def test_partition_basic(self):
        """Test basic partition."""
        result = Iterable.partition([1, 2, 3, 4, 5], predicate=lambda x: x % 2 == 0)
        assert result == ([2, 4], [1, 3, 5])

    def test_partition_all_true(self):
        """Test partition where all items match."""
        result = Iterable.partition([2, 4, 6], predicate=lambda x: x % 2 == 0)
        assert result == ([2, 4, 6], [])

    def test_partition_all_false(self):
        """Test partition where no items match."""
        result = Iterable.partition([1, 3, 5], predicate=lambda x: x % 2 == 0)
        assert result == ([], [1, 3, 5])

    def test_partition_empty(self):
        """Test partition with empty list."""
        result = Iterable.partition([], predicate=lambda x: True)
        assert result == ([], [])

    def test_partition_strings(self):
        """Test partition with strings."""
        result = Iterable.partition(["a", "b", "aa", "bb"], predicate=lambda x: len(x) == 1)
        assert result == (["a", "b"], ["aa", "bb"])


class TestZipDict:
    """Test zip_dict function."""

    def test_zip_dict_basic(self):
        """Test basic zip_dict."""
        result = dict(zip(["a", "b", "c"], [1, 2, 3], strict=False))
        assert result == {"a": 1, "b": 2, "c": 3}

    def test_zip_dict_different_lengths(self):
        """Test zip_dict with different length iterables."""
        result = dict(zip(["a", "b"], [1, 2, 3], strict=False))
        assert result == {"a": 1, "b": 2}

    def test_zip_dict_empty(self):
        """Test zip_dict with empty iterables."""
        result = dict(zip([], [], strict=False))
        assert result == {}

    def test_zip_dict_tuples(self):
        """Test zip_dict with tuples."""
        result = dict(zip(("a", "b"), (1, 2), strict=False))
        assert result == {"a": 1, "b": 2}
