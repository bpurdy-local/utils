from unittest.mock import Mock, patch

import pytest

from utils.session import Session


class TestEnhancedMetrics:
    @patch("requests.Session.request")
    def test_metrics_track_latency(self, mock_request):
        mock_request.return_value = Mock(status_code=200)

        session = Session()
        session.add_url_pattern(r"/api/users", tag="users")

        session.request("GET", "https://api.example.com/api/users")

        assert len(session.metrics["users"]["latencies"]) == 1
        assert session.metrics["users"]["latencies"][0] > 0

    @patch("requests.Session.request")
    def test_metrics_track_status_codes(self, mock_request):
        mock_request.return_value = Mock(status_code=200)

        session = Session()
        session.add_url_pattern(r"/api/users", tag="users")

        session.request("GET", "https://api.example.com/api/users")
        session.request("GET", "https://api.example.com/api/users")

        assert session.metrics["users"]["status_codes"][200] == 2

    @patch("requests.Session.request")
    def test_metrics_track_multiple_status_codes(self, mock_request):
        mock_request.side_effect = [
            Mock(status_code=200),
            Mock(status_code=404),
            Mock(status_code=200),
        ]

        session = Session()
        session.add_url_pattern(r"/api/users", tag="users")

        session.request("GET", "https://api.example.com/api/users")
        session.request("GET", "https://api.example.com/api/users/999")
        session.request("GET", "https://api.example.com/api/users/1")

        assert session.metrics["users"]["status_codes"][200] == 2
        assert session.metrics["users"]["status_codes"][404] == 1

    @patch("requests.Session.request")
    def test_metrics_track_errors(self, mock_request):
        import requests

        mock_request.side_effect = [
            requests.RequestException("Network error"),
            Mock(status_code=200),
        ]

        session = Session()
        session.add_url_pattern(r"/api/users", tag="users")

        with pytest.raises(requests.RequestException):
            session.request("GET", "https://api.example.com/api/users")

        assert session.metrics["users"]["errors"] == 1

        session.request("GET", "https://api.example.com/api/users")

        assert session.metrics["users"]["errors"] == 1
        assert session.metrics["users"]["count"] == 2

    def test_get_metrics_summary(self):
        session = Session()
        session.add_url_pattern(r"/api/users", tag="users")

        session.metrics["users"]["latencies"] = [0.1, 0.2, 0.3]
        session.metrics["users"]["count"] = 3
        session.metrics["users"]["errors"] = 1
        session.metrics["users"]["status_codes"] = {200: 2, 500: 1}

        summary = session.get_metrics_summary()

        assert summary["users"]["count"] == 3
        assert summary["users"]["errors"] == 1
        assert abs(summary["users"]["avg_latency"] - 0.2) < 0.001
        assert summary["users"]["status_codes"] == {200: 2, 500: 1}

    def test_get_metrics_summary_no_latencies(self):
        session = Session()
        session.add_url_pattern(r"/api/users", tag="users")

        summary = session.get_metrics_summary()

        assert summary["users"]["avg_latency"] == 0.0

    def test_metrics_structure(self):
        session = Session()
        session.add_url_pattern(r"/api/users", tag="users")

        assert "count" in session.metrics["users"]
        assert "latencies" in session.metrics["users"]
        assert "errors" in session.metrics["users"]
        assert "status_codes" in session.metrics["users"]

        assert session.metrics["users"]["count"] == 0
        assert session.metrics["users"]["latencies"] == []
        assert session.metrics["users"]["errors"] == 0
        assert session.metrics["users"]["status_codes"] == {}

    @patch("requests.Session.request")
    def test_compare_metrics_with_errors(self, mock_request):
        import requests

        mock_request.side_effect = [
            Mock(status_code=200),
            requests.RequestException("Error"),
            Mock(status_code=200),
        ]

        session = Session()
        session.add_url_pattern(r"/api/users", tag="users")

        snapshot = session.get_metrics()

        session.request("GET", "https://api.example.com/api/users")

        with pytest.raises(requests.RequestException):
            session.request("GET", "https://api.example.com/api/users")

        session.request("GET", "https://api.example.com/api/users")

        diff = session.compare_metrics(snapshot)

        assert diff["users"]["count"] == 3
        assert diff["users"]["errors"] == 1
