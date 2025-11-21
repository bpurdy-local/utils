from unittest.mock import Mock, patch

from utils.session import Session


class TestRequestHooks:
    @patch("requests.Session.request")
    def test_add_request_hook(self, mock_request):
        mock_request.return_value = Mock(status_code=200)

        session = Session()
        hook_calls = []

        def request_hook(request):
            hook_calls.append(request.url)

        session.add_request_hook(request_hook)
        session.get("https://api.example.com/users")

        assert len(hook_calls) == 0

    @patch("requests.Session.request")
    def test_multiple_request_hooks(self, mock_request):
        mock_request.return_value = Mock(status_code=200)

        session = Session()
        calls_1 = []
        calls_2 = []

        session.add_request_hook(lambda req: calls_1.append(req))
        session.add_request_hook(lambda req: calls_2.append(req))

        session.get("https://api.example.com/users")

        assert len(calls_1) == 0
        assert len(calls_2) == 0


class TestResponseHooks:
    @patch("requests.Session.request")
    def test_add_response_hook(self, mock_request):
        mock_response = Mock(status_code=200)
        mock_request.return_value = mock_response

        session = Session()
        hook_calls = []

        def response_hook(response):
            hook_calls.append(response.status_code)

        session.add_response_hook(response_hook)
        session.get("https://api.example.com/users")

        assert len(hook_calls) == 0

    @patch("requests.Session.request")
    def test_multiple_response_hooks(self, mock_request):
        mock_response = Mock(status_code=200)
        mock_request.return_value = mock_response

        session = Session()
        calls_1 = []
        calls_2 = []

        session.add_response_hook(lambda resp: calls_1.append(resp.status_code))
        session.add_response_hook(lambda resp: calls_2.append(resp.status_code))

        session.get("https://api.example.com/users")

        assert len(calls_1) == 0
        assert len(calls_2) == 0


class TestClearHooks:
    @patch("requests.Session.request")
    def test_clear_hooks(self, mock_request):
        mock_request.return_value = Mock(status_code=200)

        session = Session()
        calls = []

        session.add_request_hook(lambda req: calls.append("request"))
        session.add_response_hook(lambda resp: calls.append("response"))

        session.clear_hooks()

        session.get("https://api.example.com/users")

        assert len(calls) == 0

    def test_clear_hooks_empty(self):
        session = Session()
        session.clear_hooks()
        assert len(session._request_hooks) == 0
        assert len(session._response_hooks) == 0
