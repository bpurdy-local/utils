from unittest.mock import Mock, patch

import pytest

from utils.session import MemoryCache, NoCache, Session


class TestMemoryCache:
    def test_initialization(self):
        cache = MemoryCache(ttl=3600)
        assert cache.ttl == 3600
        assert cache._cache == {}

    def test_default_ttl(self):
        cache = MemoryCache()
        assert cache.ttl == 3600

    def test_set_and_get(self):
        cache = MemoryCache(ttl=3600)
        response = Mock(status_code=200)
        cache.set("key1", response, ttl=3600)

        retrieved = cache.get("key1")
        assert retrieved == response

    def test_get_nonexistent_key(self):
        cache = MemoryCache(ttl=3600)
        assert cache.get("nonexistent") is None

    @patch("time.time")
    def test_expiry(self, mock_time):
        mock_time.return_value = 1000.0
        cache = MemoryCache(ttl=10)
        response = Mock(status_code=200)
        cache.set("key1", response, ttl=10)

        mock_time.return_value = 1005.0
        assert cache.get("key1") == response

        mock_time.return_value = 1011.0
        assert cache.get("key1") is None

    def test_clear(self):
        cache = MemoryCache(ttl=3600)
        cache.set("key1", Mock(), ttl=3600)
        cache.set("key2", Mock(), ttl=3600)

        assert len(cache._cache) == 2
        cache.clear()
        assert len(cache._cache) == 0

    @patch("time.time")
    def test_cleanup_expired(self, mock_time):
        mock_time.return_value = 1000.0
        cache = MemoryCache(ttl=10)
        cache.set("key1", Mock(), ttl=10)
        cache.set("key2", Mock(), ttl=20)

        mock_time.return_value = 1015.0
        cache.cleanup_expired()

        assert "key1" not in cache._cache
        assert "key2" in cache._cache


class TestNoCache:
    def test_get_always_none(self):
        cache = NoCache()
        assert cache.get("anything") is None

    def test_set_does_nothing(self):
        cache = NoCache()
        cache.set("key", Mock(), ttl=100)
        assert cache.get("key") is None

    def test_clear_does_nothing(self):
        cache = NoCache()
        cache.clear()


class TestSessionWithCache:
    @patch("requests.Session.request")
    def test_cache_get_requests(self, mock_request):
        mock_response = Mock(status_code=200)
        mock_request.return_value = mock_response

        cache = MemoryCache(ttl=3600)
        session = Session(cache=cache)

        response1 = session.get("https://api.example.com/data")
        response2 = session.get("https://api.example.com/data")

        assert response1 == response2
        assert mock_request.call_count == 1

    @patch("requests.Session.request")
    def test_cache_respects_params(self, mock_request):
        mock_request.return_value = Mock(status_code=200)

        cache = MemoryCache(ttl=3600)
        session = Session(cache=cache)

        session.get("https://api.example.com/data", params={"id": "1"})
        session.get("https://api.example.com/data", params={"id": "2"})

        assert mock_request.call_count == 2

    @patch("requests.Session.request")
    def test_cache_only_200_responses(self, mock_request):
        mock_request.return_value = Mock(status_code=404)

        cache = MemoryCache(ttl=3600)
        session = Session(cache=cache)

        session.get("https://api.example.com/notfound")
        session.get("https://api.example.com/notfound")

        assert mock_request.call_count == 2

    @patch("requests.Session.request")
    def test_cache_only_get_requests(self, mock_request):
        mock_request.return_value = Mock(status_code=200)

        cache = MemoryCache(ttl=3600)
        session = Session(cache=cache)

        session.post("https://api.example.com/data", json={"key": "value"})
        session.post("https://api.example.com/data", json={"key": "value"})

        assert mock_request.call_count == 2

    def test_no_cache_by_default(self):
        session = Session()
        assert session._cache is None
