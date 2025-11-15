"""Comprehensive tests for Dict wrapper class."""

from utils import Dict


class TestDictPickOmit:
    """Test pick and omit methods."""

    def test_pick_basic(self):
        """Test basic pick."""
        result = Dict.pick({"a": 1, "b": 2, "c": 3}, "a", "c")
        assert result == {"a": 1, "c": 3}
        assert isinstance(result, dict)

    def test_omit_basic(self):
        """Test basic omit."""
        result = Dict.omit({"a": 1, "b": 2, "c": 3}, "a", "c")
        assert result == {"b": 2}
        assert isinstance(result, dict)

    def test_pick_missing_key(self):
        """Test pick with missing key."""
        result = Dict.pick({"a": 1, "b": 2}, "a", "c")
        assert result == {"a": 1}

    def test_omit_missing_key(self):
        """Test omit with missing key."""
        result = Dict.omit({"a": 1, "b": 2}, "c")
        assert result == {"a": 1, "b": 2}


class TestDictDeepGetSet:
    """Test deep_get and deep_set methods."""

    def test_deep_get_basic(self):
        """Test basic deep_get."""
        result = Dict.deep_get({"user": {"profile": {"name": "Alice"}}}, path="user.profile.name")
        assert result == "Alice"

    def test_deep_get_missing(self):
        """Test deep_get with missing path."""
        result = Dict.deep_get(
            {"user": {"profile": {}}}, path="user.profile.name", default="Unknown"
        )
        assert result == "Unknown"

    def test_deep_set_basic(self):
        """Test basic deep_set."""
        d = {}
        Dict.deep_set(d, path="user.profile.name", value="Alice")
        assert d["user"]["profile"]["name"] == "Alice"

    def test_deep_set_existing(self):
        """Test deep_set with existing path."""
        d = {"user": {"profile": {}}}
        Dict.deep_set(d, path="user.profile.name", value="Alice")
        assert d["user"]["profile"]["name"] == "Alice"


class TestDictMerge:
    """Test merge method."""

    def test_merge_shallow(self):
        """Test shallow merge."""
        result = Dict.merge({"a": 1, "b": 2}, other={"b": 3, "c": 4})
        assert result == {"a": 1, "b": 3, "c": 4}

    def test_merge_deep(self):
        """Test deep merge."""
        result = Dict.merge({"a": 1, "b": {"c": 2}}, other={"b": {"d": 3}, "e": 4}, deep=True)
        assert result["b"]["c"] == 2
        assert result["b"]["d"] == 3
        assert result["e"] == 4


class TestDictTransformations:
    """Test transformation methods."""

    def test_map_values(self):
        """Test map_values."""
        result = Dict.map_values({"a": 1, "b": 2, "c": 3}, func=lambda x: x * 2)
        assert result == {"a": 2, "b": 4, "c": 6}
        assert isinstance(result, dict)

    def test_map_keys(self):
        """Test map_keys."""
        result = Dict.map_keys({"a": 1, "b": 2}, func=str.upper)
        assert result == {"A": 1, "B": 2}
        assert isinstance(result, dict)

    def test_filter(self):
        """Test filter."""
        result = Dict.filter({"a": 1, "b": 2, "c": 3}, predicate=lambda k, v: v > 1)
        assert result == {"b": 2, "c": 3}
        assert isinstance(result, dict)

    def test_invert(self):
        """Test invert."""
        result = Dict.invert({"a": 1, "b": 2, "c": 3})
        assert result == {1: "a", 2: "b", 3: "c"}
        assert isinstance(result, dict)


class TestDictUtilities:
    """Test utility methods."""

    def test_defaults(self):
        """Test defaults."""
        result = Dict.defaults({"a": 1}, defaults={"b": 2, "c": 3})
        assert result == {"a": 1, "b": 2, "c": 3}
        assert isinstance(result, dict)

    def test_defaults_existing(self):
        """Test defaults with existing keys."""
        result = Dict.defaults({"a": 1, "b": 5}, defaults={"b": 2, "c": 3})
        assert result["b"] == 5

    def test_compact(self):
        """Test compact."""
        result = Dict.compact({"a": 1, "b": None, "c": 3})
        assert result == {"a": 1, "c": 3}
        assert isinstance(result, dict)


class TestDictFlatten:
    """Test flatten and unflatten methods."""

    def test_flatten_basic(self):
        """Test basic flatten."""
        result = Dict.flatten({"a": {"b": {"c": 1}}})
        assert result == {"a.b.c": 1}
        assert isinstance(result, dict)

    def test_unflatten_basic(self):
        """Test basic unflatten."""
        result = Dict.unflatten({"a.b.c": 1})
        assert result == {"a": {"b": {"c": 1}}}
        assert isinstance(result, dict)

    def test_flatten_unflatten_roundtrip(self):
        """Test flatten/unflatten roundtrip."""
        original = {"a": {"b": {"c": 1, "d": 2}}}
        flattened = Dict.flatten(original)
        unflattened = Dict.unflatten(flattened)
        assert unflattened == original
