from unittest.mock import Mock, patch

import pytest

from utils.session import BatchRequest, Session


class TestBatchRequest:
    def test_initialization(self):
        req = BatchRequest("GET", "https://api.example.com/users")
        assert req.method == "GET"
        assert req.url == "https://api.example.com/users"
        assert req.params is None
        assert req.data is None
        assert req.json is None
        assert req.headers is None

    def test_initialization_with_params(self):
        req = BatchRequest(
            "POST",
            "https://api.example.com/data",
            params={"id": "1"},
            json={"name": "test"},
            headers={"Authorization": "Bearer token"},
        )
        assert req.method == "POST"
        assert req.params == {"id": "1"}
        assert req.json == {"name": "test"}
        assert req.headers == {"Authorization": "Bearer token"}

    def test_method_uppercase(self):
        req = BatchRequest("get", "https://api.example.com/users")
        assert req.method == "GET"

    def test_get_class_method(self):
        req = BatchRequest.get("https://api.example.com/users", params={"id": "1"})
        assert req.method == "GET"
        assert req.url == "https://api.example.com/users"
        assert req.params == {"id": "1"}

    def test_post_class_method(self):
        req = BatchRequest.post("https://api.example.com/data", json={"key": "value"})
        assert req.method == "POST"
        assert req.json == {"key": "value"}

    def test_put_class_method(self):
        req = BatchRequest.put("https://api.example.com/data/1", json={"key": "value"})
        assert req.method == "PUT"

    def test_delete_class_method(self):
        req = BatchRequest.delete("https://api.example.com/data/1")
        assert req.method == "DELETE"

    def test_patch_class_method(self):
        req = BatchRequest.patch("https://api.example.com/data/1", json={"key": "value"})
        assert req.method == "PATCH"


class TestBatchExecution:
    @patch("requests.Session.request")
    def test_single_batch_request(self, mock_request):
        mock_response = Mock(status_code=200)
        mock_request.return_value = mock_response

        session = Session()
        req = BatchRequest.get("https://api.example.com/users")

        responses = session.batch_request(req)

        assert len(responses) == 1
        assert responses[0] == mock_response
        assert mock_request.call_count == 1

    @patch("requests.Session.request")
    def test_multiple_batch_requests(self, mock_request):
        mock_request.return_value = Mock(status_code=200)

        session = Session()
        req1 = BatchRequest.get("https://api.example.com/users/1")
        req2 = BatchRequest.get("https://api.example.com/users/2")
        req3 = BatchRequest.post("https://api.example.com/data", json={"key": "value"})

        responses = session.batch_request(req1, req2, req3)

        assert len(responses) == 3
        assert mock_request.call_count == 3

    @patch("requests.Session.request")
    def test_batch_request_with_list(self, mock_request):
        mock_request.return_value = Mock(status_code=200)

        session = Session()
        req1 = BatchRequest.get("https://api.example.com/users/1")
        req2 = BatchRequest.get("https://api.example.com/users/2")
        req3 = BatchRequest.get("https://api.example.com/users/3")

        responses = session.batch_request([req1, req2], req3)

        assert len(responses) == 3
        assert mock_request.call_count == 3

    @patch("requests.Session.request")
    def test_batch_request_mixed_groups(self, mock_request):
        mock_request.return_value = Mock(status_code=200)

        session = Session()
        req1 = BatchRequest.get("https://api.example.com/users/1")
        req2 = BatchRequest.get("https://api.example.com/users/2")
        req3 = BatchRequest.get("https://api.example.com/users/3")
        req4 = BatchRequest.get("https://api.example.com/users/4")

        responses = session.batch_request(req1, [req2, req3], req4)

        assert len(responses) == 4
        assert mock_request.call_count == 4

    @patch("requests.Session.request")
    def test_batch_returns_all_responses(self, mock_request):
        responses_data = [Mock(status_code=200, text=f"Response {i}") for i in range(3)]
        mock_request.side_effect = responses_data

        session = Session()
        req1 = BatchRequest.get("https://api.example.com/users/1")
        req2 = BatchRequest.get("https://api.example.com/users/2")
        req3 = BatchRequest.get("https://api.example.com/users/3")

        responses = session.batch_request(req1, req2, req3)

        assert len(responses) == 3
        response_texts = {r.text for r in responses}
        assert response_texts == {"Response 0", "Response 1", "Response 2"}
