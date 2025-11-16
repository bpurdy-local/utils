"""Comprehensive tests for Iterable wrapper class."""

import pytest

from utils import Iterable


class TestIterableChunk:
    """Test chunk method."""

    def test_chunk_basic(self):
        """Test basic chunking."""
        result = Iterable.chunk([1, 2, 3, 4, 5], size=2)
        assert len(result) == 3
        assert result[0] == [1, 2]
        assert result[1] == [3, 4]
        assert result[2] == [5]

    def test_chunk_exact_size(self):
        """Test chunking with exact size."""
        result = Iterable.chunk([1, 2, 3, 4], size=2)
        assert len(result) == 2

    def test_chunk_empty(self):
        """Test chunking empty iterable."""
        result = Iterable.chunk([], size=2)
        assert result == []


class TestIterableFlatten:
    """Test flatten method."""

    def test_flatten_basic(self):
        """Test basic flattening."""
        result = Iterable.flatten([[1, 2], [3, 4]])
        assert result == [1, 2, 3, 4]

    def test_flatten_mixed(self):
        """Test flattening with mixed types."""
        result = Iterable.flatten([[1, 2], 3, [4, 5]])
        assert result == [1, 2, 3, 4, 5]

    def test_flatten_empty(self):
        """Test flattening empty iterable."""
        result = Iterable.flatten([])
        assert result == []


class TestIterableUnique:
    """Test unique method."""

    def test_unique_basic(self):
        """Test basic uniqueness."""
        result = Iterable.unique([1, 2, 2, 3, 1])
        assert result == [1, 2, 3]

    def test_unique_with_key(self):
        """Test unique with key function."""
        items = [{"x": 1}, {"x": 2}, {"x": 1}]
        result = Iterable.unique(items, key=lambda d: d["x"])
        assert len(result) == 2

    def test_unique_empty(self):
        """Test unique with empty iterable."""
        result = Iterable.unique([])
        assert result == []


class TestIterableFirstLast:
    """Test first and last methods."""

    def test_first_basic(self):
        """Test basic first."""
        assert Iterable.first([1, 2, 3]) == 1

    def test_first_empty(self):
        """Test first with empty iterable."""
        assert Iterable.first([]) is None
        assert Iterable.first([], default=0) == 0

    def test_last_basic(self):
        """Test basic last."""
        assert Iterable.last([1, 2, 3]) == 3

    def test_last_empty(self):
        """Test last with empty iterable."""
        assert Iterable.last([]) is None
        assert Iterable.last([], default=0) == 0


class TestIterableGroupBy:
    """Test group_by method."""

    def test_group_by_basic(self):
        """Test basic grouping."""
        result = Iterable.group_by([1, 2, 3, 4], key=lambda x: x % 2)
        assert 0 in result
        assert 1 in result
        assert isinstance(result[0], list)
        assert isinstance(result[1], list)


class TestIterablePartition:
    """Test partition method."""

    def test_partition_basic(self):
        """Test basic partition."""
        true_list, false_list = Iterable.partition([1, 2, 3, 4, 5], predicate=lambda x: x % 2 == 0)
        assert true_list == [2, 4]
        assert false_list == [1, 3, 5]


class TestIterablePluck:
    """Test pluck method."""

    def test_pluck_basic(self):
        """Test basic pluck."""
        items = [{"name": "Alice"}, {"name": "Bob"}]
        result = Iterable.pluck(items, key="name")
        assert result == ["Alice", "Bob"]

    def test_pluck_missing_key(self):
        """Test pluck with missing key."""
        items = [{"name": "Alice"}, {"age": 25}]
        result = Iterable.pluck(items, key="name")
        assert result == ["Alice"]


class TestIterableCompact:
    """Test compact method."""

    def test_compact_basic(self):
        """Test basic compact."""
        result = Iterable.compact([1, None, 2, None, 3])
        assert result == [1, 2, 3]

    def test_compact_no_none(self):
        """Test compact with no None values."""
        result = Iterable.compact([1, 2, 3])
        assert result == [1, 2, 3]


class TestIterableAggregations:
    """Test aggregation methods."""

    def test_sum_by_basic(self):
        """Test basic sum_by."""
        assert Iterable.sum_by([1, 2, 3, 4]) == 10

    def test_sum_by_with_key(self):
        """Test sum_by with key function."""
        items = [{"x": 1}, {"x": 2}, {"x": 3}]
        assert Iterable.sum_by(items, key=lambda d: d["x"]) == 6

    def test_average_basic(self):
        """Test basic average."""
        assert Iterable.average([1, 2, 3, 4]) == 2.5

    def test_average_empty(self):
        """Test average with empty iterable."""
        with pytest.raises(ValueError):
            Iterable.average([])

    def test_count_by_basic(self):
        """Test basic count_by."""
        result = Iterable.count_by([1, 2, 2, 3])
        assert result == {1: 1, 2: 2, 3: 1}

    def test_count_by_with_key(self):
        """Test count_by with key function."""
        items = [{"type": "a"}, {"type": "b"}, {"type": "a"}]
        result = Iterable.count_by(items, key=lambda d: d["type"])
        assert result == {"a": 2, "b": 1}


class TestIterableSlicing:
    """Test take and drop methods."""

    def test_take_basic(self):
        """Test basic take."""
        result = Iterable.take([1, 2, 3, 4, 5], n=3)
        assert result == [1, 2, 3]

    def test_take_more_than_length(self):
        """Test take with more than length."""
        result = Iterable.take([1, 2, 3], n=10)
        assert result == [1, 2, 3]

    def test_drop_basic(self):
        """Test basic drop."""
        result = Iterable.drop([1, 2, 3, 4, 5], n=2)
        assert result == [3, 4, 5]

    def test_drop_more_than_length(self):
        """Test drop with more than length."""
        result = Iterable.drop([1, 2, 3], n=10)
        assert result == []


class TestIterableFindMethods:
    """Test find methods."""

    def test_find_first_basic(self):
        """Test find_first with basic predicate."""
        numbers = [1, 2, 3, 4, 5]
        result = Iterable.find_first(numbers, predicate=lambda x: x > 3)
        assert result == 4

    def test_find_first_no_match(self):
        """Test find_first with no match."""
        numbers = [1, 2, 3, 4, 5]
        result = Iterable.find_first(numbers, predicate=lambda x: x > 10)
        assert result is None

    def test_find_first_empty_list(self):
        """Test find_first with empty list."""
        result = Iterable.find_first([], predicate=lambda x: x > 0)
        assert result is None

    def test_find_first_dict_predicate(self):
        """Test find_first with dict predicate."""
        users = [{"name": "Alice", "age": 30}, {"name": "Bob", "age": 25}]
        result = Iterable.find_first(users, predicate=lambda u: u["age"] > 28)
        assert result == {"name": "Alice", "age": 30}

    def test_find_first_returns_first_match(self):
        """Test find_first returns first match when multiple exist."""
        numbers = [1, 4, 2, 5, 3, 6]
        result = Iterable.find_first(numbers, predicate=lambda x: x > 3)
        assert result == 4  # First match, not 5 or 6

    def test_find_first_type_preservation(self):
        """Test find_first preserves type."""
        strings = ["apple", "banana", "cherry"]
        result = Iterable.find_first(strings, predicate=lambda s: "a" in s)
        assert isinstance(result, str)
        assert result == "apple"

    def test_find_last_basic(self):
        """Test find_last with basic predicate."""
        numbers = [1, 2, 3, 4, 5, 4, 3]
        result = Iterable.find_last(numbers, predicate=lambda x: x == 4)
        assert result == 4

    def test_find_last_no_match(self):
        """Test find_last with no match."""
        numbers = [1, 2, 3, 4, 5]
        result = Iterable.find_last(numbers, predicate=lambda x: x > 10)
        assert result is None

    def test_find_last_empty_list(self):
        """Test find_last with empty list."""
        result = Iterable.find_last([], predicate=lambda x: x > 0)
        assert result is None

    def test_find_last_returns_last_match(self):
        """Test find_last returns last match when multiple exist."""
        numbers = [1, 4, 2, 5, 3, 6]
        result = Iterable.find_last(numbers, predicate=lambda x: x > 3)
        assert result == 6  # Last match, not 4 or 5

    def test_find_last_dict_predicate(self):
        """Test find_last with dict predicate."""
        users = [
            {"name": "Alice", "age": 30},
            {"name": "Bob", "age": 25},
            {"name": "Charlie", "age": 35},
        ]
        result = Iterable.find_last(users, predicate=lambda u: u["age"] > 28)
        assert result == {"name": "Charlie", "age": 35}

    def test_find_all_basic(self):
        """Test find_all with basic predicate."""
        numbers = [1, 2, 3, 4, 5]
        result = Iterable.find_all(numbers, predicate=lambda x: x > 3)
        assert result == [4, 5]

    def test_find_all_no_matches(self):
        """Test find_all with no matches."""
        numbers = [1, 2, 3, 4, 5]
        result = Iterable.find_all(numbers, predicate=lambda x: x > 10)
        assert result == []
        assert isinstance(result, list)

    def test_find_all_empty_list(self):
        """Test find_all with empty list."""
        result = Iterable.find_all([], predicate=lambda x: x > 0)
        assert result == []

    def test_find_all_all_match(self):
        """Test find_all when all items match."""
        numbers = [2, 4, 6, 8]
        result = Iterable.find_all(numbers, predicate=lambda x: x % 2 == 0)
        assert result == [2, 4, 6, 8]

    def test_find_all_some_match(self):
        """Test find_all when some items match."""
        numbers = [1, 2, 3, 4, 5, 6]
        result = Iterable.find_all(numbers, predicate=lambda x: x % 2 == 0)
        assert result == [2, 4, 6]

    def test_find_all_preserves_order(self):
        """Test find_all preserves order."""
        numbers = [5, 1, 4, 2, 6, 3]
        result = Iterable.find_all(numbers, predicate=lambda x: x > 3)
        assert result == [5, 4, 6]

    def test_find_all_dict_predicate(self):
        """Test find_all with dict predicate."""
        users = [
            {"name": "Alice", "age": 30},
            {"name": "Bob", "age": 25},
            {"name": "Charlie", "age": 35},
        ]
        result = Iterable.find_all(users, predicate=lambda u: u["age"] > 28)
        assert result == [{"name": "Alice", "age": 30}, {"name": "Charlie", "age": 35}]

    def test_find_methods_with_complex_predicate(self):
        """Test find methods with complex predicate."""
        data = [
            {"id": 1, "status": "active", "score": 85},
            {"id": 2, "status": "inactive", "score": 92},
            {"id": 3, "status": "active", "score": 78},
        ]

        # find_first
        first = Iterable.find_first(
            data, predicate=lambda x: x["status"] == "active" and x["score"] > 80
        )
        assert first == {"id": 1, "status": "active", "score": 85}

        # find_all
        all_active = Iterable.find_all(data, predicate=lambda x: x["status"] == "active")
        assert len(all_active) == 2
