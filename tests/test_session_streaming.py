import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from utils.session import Session


class TestStreamDownload:
    @patch("requests.Session.get")
    def test_stream_download_basic(self, mock_get):
        mock_response = Mock()
        mock_response.__enter__ = Mock(return_value=mock_response)
        mock_response.__exit__ = Mock(return_value=False)
        mock_response.raise_for_status = Mock()
        mock_response.iter_content = Mock(return_value=[b"chunk1", b"chunk2", b"chunk3"])
        mock_get.return_value = mock_response

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "downloaded_file.txt"

            session = Session()
            session.stream_download("https://example.com/file.txt", output_path=str(output_path))

            assert output_path.exists()
            content = output_path.read_bytes()
            assert content == b"chunk1chunk2chunk3"

    @patch("requests.Session.get")
    def test_stream_download_creates_directory(self, mock_get):
        mock_response = Mock()
        mock_response.__enter__ = Mock(return_value=mock_response)
        mock_response.__exit__ = Mock(return_value=False)
        mock_response.raise_for_status = Mock()
        mock_response.iter_content = Mock(return_value=[b"data"])
        mock_get.return_value = mock_response

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "nested" / "dir" / "file.txt"

            session = Session()
            session.stream_download("https://example.com/file.txt", output_path=str(output_path))

            assert output_path.exists()
            assert output_path.parent.exists()

    @patch("requests.Session.get")
    def test_stream_download_custom_chunk_size(self, mock_get):
        mock_response = Mock()
        mock_response.__enter__ = Mock(return_value=mock_response)
        mock_response.__exit__ = Mock(return_value=False)
        mock_response.raise_for_status = Mock()
        mock_response.iter_content = Mock(return_value=[b"data"])
        mock_get.return_value = mock_response

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "file.txt"

            session = Session()
            session.stream_download(
                "https://example.com/file.txt", output_path=str(output_path), chunk_size=4096
            )

            mock_response.iter_content.assert_called_once_with(chunk_size=4096)

    @patch("requests.Session.get")
    def test_stream_download_with_path_object(self, mock_get):
        mock_response = Mock()
        mock_response.__enter__ = Mock(return_value=mock_response)
        mock_response.__exit__ = Mock(return_value=False)
        mock_response.raise_for_status = Mock()
        mock_response.iter_content = Mock(return_value=[b"test"])
        mock_get.return_value = mock_response

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "file.txt"

            session = Session()
            session.stream_download("https://example.com/file.txt", output_path=output_path)

            assert output_path.exists()
            assert output_path.read_bytes() == b"test"

    @patch("requests.Session.get")
    def test_stream_download_empty_chunks_skipped(self, mock_get):
        mock_response = Mock()
        mock_response.__enter__ = Mock(return_value=mock_response)
        mock_response.__exit__ = Mock(return_value=False)
        mock_response.raise_for_status = Mock()
        mock_response.iter_content = Mock(return_value=[b"chunk1", b"", b"chunk2", None, b"chunk3"])
        mock_get.return_value = mock_response

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "file.txt"

            session = Session()
            session.stream_download("https://example.com/file.txt", output_path=str(output_path))

            content = output_path.read_bytes()
            assert content == b"chunk1chunk2chunk3"

    @patch("requests.Session.get")
    def test_stream_download_raises_on_http_error(self, mock_get):
        import requests

        mock_response = Mock()
        mock_response.__enter__ = Mock(return_value=mock_response)
        mock_response.__exit__ = Mock(return_value=False)
        mock_response.raise_for_status = Mock(side_effect=requests.HTTPError("404 Not Found"))
        mock_get.return_value = mock_response

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "file.txt"

            session = Session()
            with pytest.raises(requests.HTTPError):
                session.stream_download(
                    "https://example.com/missing.txt", output_path=str(output_path)
                )
