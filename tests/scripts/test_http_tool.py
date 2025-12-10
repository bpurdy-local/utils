"""Tests for http_tool.py."""

import argparse
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

# Import the script module
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts"))
import http_tool


class TestParseHeaders:
    """Tests for parse_headers function."""

    def test_parse_single_header(self):
        """Test parsing single header."""
        result = http_tool.parse_headers(["Content-Type: application/json"])
        assert result == {"Content-Type": "application/json"}

    def test_parse_multiple_headers(self):
        """Test parsing multiple headers."""
        result = http_tool.parse_headers([
            "Authorization: Bearer token",
            "X-Custom: value",
        ])
        assert result == {
            "Authorization": "Bearer token",
            "X-Custom": "value",
        }

    def test_parse_empty(self):
        """Test parsing empty headers."""
        result = http_tool.parse_headers(None)
        assert result == {}


class TestParseData:
    """Tests for parse_data function."""

    def test_parse_json(self):
        """Test parsing JSON data."""
        data, json_data = http_tool.parse_data(None, '{"key": "value"}')
        assert data is None
        assert json_data == {"key": "value"}

    def test_parse_form_data(self):
        """Test parsing form data."""
        data, json_data = http_tool.parse_data("user=john&pass=secret", None, form=True)
        assert data == {"user": "john", "pass": "secret"}
        assert json_data is None

    def test_parse_raw_data(self):
        """Test parsing raw data."""
        data, json_data = http_tool.parse_data("raw data", None, form=False)
        assert data == "raw data"
        assert json_data is None


class TestFormatResponse:
    """Tests for format_response function."""

    def test_format_json_response(self):
        """Test formatting JSON response."""
        response = MagicMock()
        response.status_code = 200
        response.reason = "OK"
        response.ok = True
        response.headers = {"content-type": "application/json"}
        response.text = '{"result": "success"}'

        result = http_tool.format_response(response, verbose=False, headers_only=False)
        assert "result" in result
        assert "success" in result

    def test_format_with_headers(self):
        """Test formatting with headers."""
        response = MagicMock()
        response.status_code = 200
        response.reason = "OK"
        response.ok = True
        response.headers = {"Content-Type": "text/html"}
        response.text = "<html></html>"

        result = http_tool.format_response(response, verbose=True, headers_only=False)
        assert "HTTP 200 OK" in result
        assert "Content-Type" in result


class TestCmdGet:
    """Tests for cmd_get function."""

    @patch("http_tool.Session")
    def test_get_request(self, mock_session_class, capsys):
        """Test GET request."""
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.ok = True
        mock_response.headers = {"content-type": "text/plain"}
        mock_response.text = "Hello World"
        mock_session.get.return_value = mock_response
        mock_session_class.return_value = mock_session

        args = argparse.Namespace(
            url="https://example.com",
            header=None,
            query=None,
            bearer=None,
            verbose=False,
            headers=False,
            output=None,
            timeout=30,
        )
        result = http_tool.cmd_get(args)
        assert result == 0
        captured = capsys.readouterr()
        assert "Hello World" in captured.out


class TestCmdPost:
    """Tests for cmd_post function."""

    @patch("http_tool.Session")
    def test_post_request(self, mock_session_class, capsys):
        """Test POST request."""
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.ok = True
        mock_response.headers = {"content-type": "application/json"}
        mock_response.text = '{"id": 1}'
        mock_session.post.return_value = mock_response
        mock_session_class.return_value = mock_session

        args = argparse.Namespace(
            url="https://example.com/api",
            header=None,
            data=None,
            json='{"name": "test"}',
            form=False,
            bearer=None,
            verbose=False,
            headers=False,
            output=None,
            timeout=30,
        )
        result = http_tool.cmd_post(args)
        assert result == 0


class TestCmdHead:
    """Tests for cmd_head function."""

    @patch("http_tool.Session")
    def test_head_request(self, mock_session_class, capsys):
        """Test HEAD request."""
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.reason = "OK"
        mock_response.ok = True
        mock_response.headers = {"Content-Length": "12345"}
        mock_session.head.return_value = mock_response
        mock_session_class.return_value = mock_session

        args = argparse.Namespace(
            url="https://example.com",
            header=None,
            timeout=30,
        )
        result = http_tool.cmd_head(args)
        assert result == 0
        captured = capsys.readouterr()
        assert "HTTP 200 OK" in captured.out
        assert "Content-Length" in captured.out
