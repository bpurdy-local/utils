import datetime
import json

import pytest

from utils.json_encoder import JsonEncoder


def test_tuple_conversion():
    data = {"coords": (10, 20, 30)}
    result = json.dumps(data, cls=JsonEncoder)
    parsed = json.loads(result)
    assert parsed["coords"] == [10, 20, 30]


def test_empty_tuple():
    data = {"empty": ()}
    result = json.dumps(data, cls=JsonEncoder)
    parsed = json.loads(result)
    assert parsed["empty"] == []


def test_nested_tuples():
    data = {"nested": ((1, 2), (3, 4))}
    result = json.dumps(data, cls=JsonEncoder)
    parsed = json.loads(result)
    assert parsed["nested"] == [[1, 2], [3, 4]]


def test_set_conversion():
    data = {"tags": {1, 2, 3}}
    result = json.dumps(data, cls=JsonEncoder)
    parsed = json.loads(result)
    assert set(parsed["tags"]) == {1, 2, 3}


def test_set_with_strings():
    data = {"tags": {"python", "logging", "json"}}
    result = json.dumps(data, cls=JsonEncoder)
    parsed = json.loads(result)
    assert set(parsed["tags"]) == {"python", "logging", "json"}


def test_datetime_conversion():
    dt = datetime.datetime(2025, 11, 15, 10, 30, 0)
    data = {"timestamp": dt}
    result = json.dumps(data, cls=JsonEncoder)
    parsed = json.loads(result)
    assert parsed["timestamp"] == "2025-11-15T10:30:00"


def test_date_conversion():
    d = datetime.date(2025, 11, 15)
    data = {"date": d}
    result = json.dumps(data, cls=JsonEncoder)
    parsed = json.loads(result)
    assert parsed["date"] == "2025-11-15"


def test_arrow_datetime_conversion():
    try:
        import arrow

        dt = arrow.get("2025-11-15T10:30:00+00:00")
        data = {"timestamp": dt}
        result = json.dumps(data, cls=JsonEncoder)
        parsed = json.loads(result)
        assert "2025-11-15" in parsed["timestamp"]
        assert "10:30:00" in parsed["timestamp"]
    except ImportError:
        pytest.skip("Arrow not installed")


def test_custom_object_with_to_dict():
    class User:
        def to_dict(self):
            return {"id": 123, "name": "Alice"}

    data = {"user": User()}
    result = json.dumps(data, cls=JsonEncoder)
    parsed = json.loads(result)
    assert parsed["user"] == {"id": 123, "name": "Alice"}


def test_custom_object_with_dict_attribute():
    class Point:
        def __init__(self, x, y):
            self.x = x
            self.y = y

    data = {"point": Point(10, 20)}
    result = json.dumps(data, cls=JsonEncoder)
    parsed = json.loads(result)
    assert parsed["point"] == {"x": 10, "y": 20}


def test_custom_object_fallback_to_str():
    class CustomType:
        __slots__ = ()

        def __str__(self):
            return "custom_value"

    data = {"value": CustomType()}
    result = json.dumps(data, cls=JsonEncoder)
    parsed = json.loads(result)
    assert parsed["value"] == "custom_value"


def test_object_without_to_dict_or_dict():
    obj = object()
    data = {"obj": obj}
    result = json.dumps(data, cls=JsonEncoder)
    parsed = json.loads(result)
    assert "<object object at" in parsed["obj"]


def test_nested_structures():
    data = {
        "tuples": [(1, 2), (3, 4)],
        "sets": [{"a", "b"}, {"c", "d"}],
        "mixed": {"coords": (10, 20), "tags": {"python", "test"}},
    }
    result = json.dumps(data, cls=JsonEncoder)
    parsed = json.loads(result)
    assert parsed["tuples"] == [[1, 2], [3, 4]]
    assert len(parsed["sets"]) == 2
    assert parsed["mixed"]["coords"] == [10, 20]


def test_dict_with_tuple_keys_and_set_values():
    data = {"data": [{"position": (1, 2, 3), "tags": {"a", "b", "c"}}]}
    result = json.dumps(data, cls=JsonEncoder)
    parsed = json.loads(result)
    assert parsed["data"][0]["position"] == [1, 2, 3]


def test_none_values():
    data = {"value": None, "tuple": (None, 1, 2), "set": {None, "a"}}
    result = json.dumps(data, cls=JsonEncoder)
    parsed = json.loads(result)
    assert parsed["value"] is None
    assert None in parsed["tuple"]


def test_encoder_with_standard_types():
    data = {
        "string": "hello",
        "int": 42,
        "float": 3.14,
        "bool": True,
        "list": [1, 2, 3],
        "dict": {"nested": "value"},
    }
    result = json.dumps(data, cls=JsonEncoder)
    parsed = json.loads(result)
    assert parsed == data


def test_complex_nested_structure():
    class User:
        def __init__(self, name):
            self.name = name
            self.created_at = datetime.datetime(2025, 11, 15, 10, 0, 0)

    data = {
        "users": [User("Alice"), User("Bob")],
        "metadata": {
            "tags": {"python", "testing"},
            "coordinates": (40.7128, -74.0060),
            "timestamp": datetime.date(2025, 11, 15),
        },
    }
    result = json.dumps(data, cls=JsonEncoder)
    parsed = json.loads(result)
    assert parsed["users"][0]["name"] == "Alice"
    assert parsed["metadata"]["coordinates"] == [40.7128, -74.0060]
