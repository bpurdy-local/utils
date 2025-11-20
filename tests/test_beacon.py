import threading
import time
from datetime import timedelta

import pytest

from utils.beacon import Beacon


@pytest.fixture(autouse=True)
def clear_beacon():
    Beacon.clear()
    Beacon.reset_stats()
    yield
    Beacon.clear()
    Beacon.reset_stats()


class TestBeaconBasicOperations:

    def test_register_and_get(self):
        Beacon.register("api_key", "secret123")
        value = Beacon.get("api_key")
        assert value == "secret123"

    def test_get_nonexistent_returns_none(self):
        value = Beacon.get("nonexistent")
        assert value is None

    def test_get_with_default(self):
        value = Beacon.get("nonexistent", default="fallback")
        assert value == "fallback"

    def test_get_required_raises_when_missing(self):
        with pytest.raises(KeyError, match="Beacon key 'missing' is required but not found"):
            Beacon.get("missing", required=True)

    def test_get_required_returns_value_when_present(self):
        Beacon.register("key", "value")
        value = Beacon.get("key", required=True)
        assert value == "value"

    def test_has_existing_key(self):
        Beacon.register("key", "value")
        assert Beacon.has("key") is True

    def test_has_nonexistent_key(self):
        assert Beacon.has("nonexistent") is False

    def test_unregister_existing_key(self):
        Beacon.register("key", "value")
        result = Beacon.unregister("key")
        assert result is True
        assert Beacon.has("key") is False

    def test_unregister_nonexistent_key(self):
        result = Beacon.unregister("nonexistent")
        assert result is False

    def test_clear_all_keys(self):
        Beacon.register("key1", "value1")
        Beacon.register("key2", "value2")
        Beacon.clear()
        assert Beacon.has("key1") is False
        assert Beacon.has("key2") is False

    def test_list_keys_empty(self):
        keys = Beacon.list_keys()
        assert keys == []

    def test_list_keys_with_values(self):
        Beacon.register("key1", "value1")
        Beacon.register("key2", "value2")
        keys = Beacon.list_keys()
        assert set(keys) == {"key1", "key2"}

    def test_overwrite_existing_value(self):
        Beacon.register("key", "value1")
        Beacon.register("key", "value2")
        value = Beacon.get("key")
        assert value == "value2"


class TestBeaconNamespaces:

    def test_register_with_namespace(self):
        Beacon.register("api_key", "secret", namespace="aws")
        value = Beacon.get("api_key", namespace="aws")
        assert value == "secret"

    def test_namespace_isolation(self):
        Beacon.register("key", "value1", namespace="ns1")
        Beacon.register("key", "value2", namespace="ns2")

        value1 = Beacon.get("key", namespace="ns1")
        value2 = Beacon.get("key", namespace="ns2")

        assert value1 == "value1"
        assert value2 == "value2"

    def test_has_with_namespace(self):
        Beacon.register("key", "value", namespace="ns")
        assert Beacon.has("key", namespace="ns") is True
        assert Beacon.has("key") is False

    def test_unregister_with_namespace(self):
        Beacon.register("key", "value", namespace="ns")
        result = Beacon.unregister("key", namespace="ns")
        assert result is True
        assert Beacon.has("key", namespace="ns") is False

    def test_list_keys_with_namespace_filter(self):
        Beacon.register("key1", "value1", namespace="aws")
        Beacon.register("key2", "value2", namespace="aws")
        Beacon.register("key3", "value3", namespace="gcp")

        keys = Beacon.list_keys(namespace="aws")
        assert set(keys) == {"aws:key1", "aws:key2"}

    def test_get_namespace(self):
        Beacon.register("key1", "value1", namespace="aws")
        Beacon.register("key2", "value2", namespace="aws")
        Beacon.register("key3", "value3", namespace="gcp")

        aws_values = Beacon.get_namespace("aws")
        assert aws_values == {"key1": "value1", "key2": "value2"}

    def test_get_namespace_empty(self):
        values = Beacon.get_namespace("nonexistent")
        assert values == {}

    def test_clear_namespace(self):
        Beacon.register("key1", "value1", namespace="aws")
        Beacon.register("key2", "value2", namespace="aws")
        Beacon.register("key3", "value3", namespace="gcp")

        count = Beacon.clear_namespace("aws")
        assert count == 2
        assert Beacon.has("key1", namespace="aws") is False
        assert Beacon.has("key2", namespace="aws") is False
        assert Beacon.has("key3", namespace="gcp") is True

    def test_clear_namespace_nonexistent(self):
        count = Beacon.clear_namespace("nonexistent")
        assert count == 0


class TestBeaconValueTypes:

    def test_store_string(self):
        Beacon.register("key", "string_value")
        assert Beacon.get("key") == "string_value"

    def test_store_integer(self):
        Beacon.register("key", 42)
        assert Beacon.get("key") == 42

    def test_store_float(self):
        Beacon.register("key", 3.14)
        assert Beacon.get("key") == 3.14

    def test_store_boolean(self):
        Beacon.register("key", True)
        assert Beacon.get("key") is True

    def test_store_none(self):
        Beacon.register("key", None)
        assert Beacon.get("key") is None

    def test_store_list(self):
        Beacon.register("key", [1, 2, 3])
        assert Beacon.get("key") == [1, 2, 3]

    def test_store_dict(self):
        Beacon.register("key", {"nested": "value"})
        assert Beacon.get("key") == {"nested": "value"}

    def test_store_object(self):
        class CustomObject:
            def __init__(self, value):
                self.value = value

        obj = CustomObject(42)
        Beacon.register("key", obj)
        retrieved = Beacon.get("key")
        assert retrieved.value == 42


class TestBeaconEdgeCases:

    def test_empty_string_key(self):
        Beacon.register("", "value")
        assert Beacon.get("") == "value"

    def test_empty_string_value(self):
        Beacon.register("key", "")
        assert Beacon.get("key") == ""

    def test_empty_string_namespace(self):
        Beacon.register("key", "value", namespace="")
        assert Beacon.get("key", namespace="") == "value"

    def test_colon_in_key_without_namespace(self):
        Beacon.register("key:with:colons", "value")
        assert Beacon.get("key:with:colons") == "value"

    def test_special_characters_in_key(self):
        Beacon.register("key-with_special.chars@123", "value")
        assert Beacon.get("key-with_special.chars@123") == "value"

    def test_unicode_key(self):
        Beacon.register("键", "值")
        assert Beacon.get("键") == "值"

    def test_unicode_value(self):
        Beacon.register("key", "日本語")
        assert Beacon.get("key") == "日本語"


class TestBeaconThreadSafety:

    def test_concurrent_register(self):
        def register_values(start, count):
            for i in range(start, start + count):
                Beacon.register(f"key{i}", f"value{i}")

        thread1 = threading.Thread(target=register_values, args=(0, 100))
        thread2 = threading.Thread(target=register_values, args=(100, 100))

        thread1.start()
        thread2.start()
        thread1.join()
        thread2.join()

        for i in range(200):
            assert Beacon.get(f"key{i}") == f"value{i}"

    def test_concurrent_read_write(self):
        Beacon.register("counter", 0)
        results = []

        def read_values():
            for _ in range(50):
                value = Beacon.get("counter")
                results.append(value)
                time.sleep(0.001)

        def write_values():
            for i in range(50):
                Beacon.register("counter", i)
                time.sleep(0.001)

        reader = threading.Thread(target=read_values)
        writer = threading.Thread(target=write_values)

        reader.start()
        writer.start()
        reader.join()
        writer.join()

        assert len(results) == 50

    def test_concurrent_namespace_operations(self):
        def register_namespace(ns, count):
            for i in range(count):
                Beacon.register(f"key{i}", f"value{i}", namespace=ns)

        thread1 = threading.Thread(target=register_namespace, args=("ns1", 50))
        thread2 = threading.Thread(target=register_namespace, args=("ns2", 50))

        thread1.start()
        thread2.start()
        thread1.join()
        thread2.join()

        ns1_values = Beacon.get_namespace("ns1")
        ns2_values = Beacon.get_namespace("ns2")

        assert len(ns1_values) == 50
        assert len(ns2_values) == 50


class TestBeaconTTL:

    def test_register_with_ttl(self):
        Beacon.register("key", "value", ttl=timedelta(seconds=1))
        assert Beacon.get("key") == "value"

    def test_expired_key_returns_default(self):
        Beacon.register("key", "value", ttl=timedelta(seconds=1))
        time.sleep(1.1)
        assert Beacon.get("key") is None

    def test_expired_key_has_returns_false(self):
        Beacon.register("key", "value", ttl=timedelta(seconds=1))
        time.sleep(1.1)
        assert Beacon.has("key") is False

    def test_clear_expired(self):
        Beacon.register("key1", "value1", ttl=timedelta(seconds=1))
        Beacon.register("key2", "value2")  # No TTL
        time.sleep(1.1)
        count = Beacon.clear_expired()
        assert count == 1
        assert Beacon.has("key1") is False
        assert Beacon.has("key2") is True

    def test_zero_ttl_expires_immediately(self):
        Beacon.register("key", "value", ttl=timedelta(seconds=0))
        assert Beacon.get("key") is None

    def test_negative_ttl_expires_immediately(self):
        Beacon.register("key", "value", ttl=timedelta(seconds=-1))
        assert Beacon.get("key") is None

    def test_ttl_with_namespace(self):
        Beacon.register("key", "value", namespace="ns", ttl=timedelta(seconds=1))
        assert Beacon.get("key", namespace="ns") == "value"
        time.sleep(1.1)
        assert Beacon.get("key", namespace="ns") is None

    def test_list_keys_excludes_expired(self):
        Beacon.register("key1", "value1", ttl=timedelta(seconds=1))
        Beacon.register("key2", "value2")
        time.sleep(1.1)
        keys = Beacon.list_keys()
        assert "key1" not in keys
        assert "key2" in keys

    def test_get_namespace_excludes_expired(self):
        Beacon.register("key1", "value1", namespace="ns", ttl=timedelta(seconds=1))
        Beacon.register("key2", "value2", namespace="ns")
        time.sleep(1.1)
        values = Beacon.get_namespace("ns")
        assert "key1" not in values
        assert "key2" in values

    def test_ttl_with_timedelta_seconds(self):
        Beacon.register("key", "value", ttl=timedelta(seconds=1))
        assert Beacon.get("key") == "value"
        time.sleep(1.1)
        assert Beacon.get("key") is None

    def test_ttl_with_timedelta_minutes(self):
        # Short duration for testing
        Beacon.register("key", "value", ttl=timedelta(seconds=0.5))
        assert Beacon.get("key") == "value"
        time.sleep(0.6)
        assert Beacon.get("key") is None

    def test_ttl_with_timedelta_hours(self):
        # Use a very short timedelta for testing purposes
        Beacon.register("key", "value", ttl=timedelta(milliseconds=500))
        assert Beacon.get("key") == "value"
        time.sleep(0.6)
        assert Beacon.get("key") is None

    def test_ttl_timedelta_with_namespace(self):
        Beacon.register("key", "value", namespace="ns", ttl=timedelta(seconds=1))
        assert Beacon.get("key", namespace="ns") == "value"
        time.sleep(1.1)
        assert Beacon.get("key", namespace="ns") is None


class TestBeaconStatistics:

    def test_stats_tracking(self):
        Beacon.register("key", "value")
        Beacon.get("key")  # Hit
        Beacon.get("missing")  # Miss

        stats = Beacon.stats()
        assert stats["hits"] == 1
        assert stats["misses"] == 1
        assert stats["size"] == 1

    def test_reset_stats(self):
        Beacon.register("key", "value")
        Beacon.get("key")
        Beacon.reset_stats()

        stats = Beacon.stats()
        assert stats["hits"] == 0
        assert stats["misses"] == 0

    def test_expired_counts_as_miss(self):
        Beacon.register("key", "value", ttl=timedelta(seconds=1))
        time.sleep(1.1)
        Beacon.get("key")

        stats = Beacon.stats()
        assert stats["misses"] == 1

    def test_has_does_not_affect_stats(self):
        Beacon.register("key", "value")
        Beacon.has("key")

        stats = Beacon.stats()
        assert stats["hits"] == 0
        assert stats["misses"] == 0
