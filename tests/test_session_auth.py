"""Tests for session authentication classes."""

import base64

from utils.session import APIKeyAuth, BasicAuth, BearerAuth, Session, TokenAuth


class TestBearerAuth:
    """Test BearerAuth class."""

    def test_initialization(self):
        """Test BearerAuth initialization."""
        auth = BearerAuth("test-token-123")
        assert auth.token == "test-token-123"

    def test_apply_to_session(self):
        """Test applying bearer auth to session."""
        session = Session()
        auth = BearerAuth("my-bearer-token")
        auth.apply(session)

        assert "Authorization" in session.headers
        assert session.headers["Authorization"] == "Bearer my-bearer-token"

    def test_empty_token(self):
        """Test with empty token."""
        session = Session()
        auth = BearerAuth("")
        auth.apply(session)

        assert session.headers["Authorization"] == "Bearer "


class TestBasicAuth:
    """Test BasicAuth class."""

    def test_initialization(self):
        """Test BasicAuth initialization."""
        auth = BasicAuth("username", "password")
        assert auth.username == "username"
        assert auth.password == "password"

    def test_apply_to_session(self):
        """Test applying basic auth to session."""
        session = Session()
        auth = BasicAuth("testuser", "testpass")
        auth.apply(session)

        assert "Authorization" in session.headers
        # Decode and verify credentials
        auth_value = session.headers["Authorization"]
        assert auth_value.startswith("Basic ")

        encoded = auth_value.split(" ")[1]
        decoded = base64.b64decode(encoded).decode("ascii")
        assert decoded == "testuser:testpass"

    def test_encoding_correctness(self):
        """Test that encoding matches expected format."""
        session = Session()
        auth = BasicAuth("alice", "secret123")
        auth.apply(session)

        expected = base64.b64encode(b"alice:secret123").decode("ascii")
        actual = session.headers["Authorization"].split(" ")[1]
        assert actual == expected

    def test_special_characters(self):
        """Test with special characters in credentials."""
        session = Session()
        auth = BasicAuth("user@example.com", "p@ss:word!")
        auth.apply(session)

        auth_value = session.headers["Authorization"]
        encoded = auth_value.split(" ")[1]
        decoded = base64.b64decode(encoded).decode("ascii")
        assert decoded == "user@example.com:p@ss:word!"


class TestAPIKeyAuth:
    """Test APIKeyAuth class."""

    def test_initialization_default_header(self):
        """Test APIKeyAuth initialization with default header."""
        auth = APIKeyAuth("my-api-key-123")
        assert auth.api_key == "my-api-key-123"
        assert auth.header_name == "X-API-Key"

    def test_initialization_custom_header(self):
        """Test APIKeyAuth initialization with custom header."""
        auth = APIKeyAuth("my-key", header_name="X-Custom-Key")
        assert auth.api_key == "my-key"
        assert auth.header_name == "X-Custom-Key"

    def test_apply_to_session_default_header(self):
        """Test applying API key auth with default header."""
        session = Session()
        auth = APIKeyAuth("secret-key-456")
        auth.apply(session)

        assert "X-API-Key" in session.headers
        assert session.headers["X-API-Key"] == "secret-key-456"

    def test_apply_to_session_custom_header(self):
        """Test applying API key auth with custom header."""
        session = Session()
        auth = APIKeyAuth("custom-key-789", header_name="X-Custom-API-Key")
        auth.apply(session)

        assert "X-Custom-API-Key" in session.headers
        assert session.headers["X-Custom-API-Key"] == "custom-key-789"

    def test_multiple_api_keys(self):
        """Test setting multiple API keys with different headers."""
        session = Session()
        auth1 = APIKeyAuth("key1", header_name="X-API-Key-1")
        auth2 = APIKeyAuth("key2", header_name="X-API-Key-2")

        auth1.apply(session)
        auth2.apply(session)

        assert session.headers["X-API-Key-1"] == "key1"
        assert session.headers["X-API-Key-2"] == "key2"


class TestTokenAuth:
    """Test TokenAuth class."""

    def test_initialization_default_scheme(self):
        """Test TokenAuth initialization with default scheme."""
        auth = TokenAuth("my-token-123")
        assert auth.token == "my-token-123"
        assert auth.scheme == "Token"

    def test_initialization_custom_scheme(self):
        """Test TokenAuth initialization with custom scheme."""
        auth = TokenAuth("my-token", scheme="CustomScheme")
        assert auth.token == "my-token"
        assert auth.scheme == "CustomScheme"

    def test_apply_to_session_default_scheme(self):
        """Test applying token auth with default scheme."""
        session = Session()
        auth = TokenAuth("token-456")
        auth.apply(session)

        assert "Authorization" in session.headers
        assert session.headers["Authorization"] == "Token token-456"

    def test_apply_to_session_custom_scheme(self):
        """Test applying token auth with custom scheme."""
        session = Session()
        auth = TokenAuth("token-789", scheme="JWT")
        auth.apply(session)

        assert session.headers["Authorization"] == "JWT token-789"

    def test_bearer_equivalent(self):
        """Test that TokenAuth with scheme='Bearer' equals BearerAuth."""
        session1 = Session()
        session2 = Session()

        token_auth = TokenAuth("test-token", scheme="Bearer")
        bearer_auth = BearerAuth("test-token")

        token_auth.apply(session1)
        bearer_auth.apply(session2)

        assert session1.headers["Authorization"] == session2.headers["Authorization"]


class TestAuthIntegration:
    """Test authentication integration with Session class."""

    def test_session_set_auth_bearer(self):
        """Test Session.set_auth() with BearerAuth."""
        session = Session()
        auth = BearerAuth("integration-token")
        session.set_auth(auth)

        assert session.headers["Authorization"] == "Bearer integration-token"

    def test_session_set_auth_basic(self):
        """Test Session.set_auth() with BasicAuth."""
        session = Session()
        auth = BasicAuth("user", "pass")
        session.set_auth(auth)

        assert "Authorization" in session.headers
        assert session.headers["Authorization"].startswith("Basic ")

    def test_session_set_auth_api_key(self):
        """Test Session.set_auth() with APIKeyAuth."""
        session = Session()
        auth = APIKeyAuth("api-key-123")
        session.set_auth(auth)

        assert session.headers["X-API-Key"] == "api-key-123"

    def test_session_set_auth_token(self):
        """Test Session.set_auth() with TokenAuth."""
        session = Session()
        auth = TokenAuth("custom-token", scheme="CustomScheme")
        session.set_auth(auth)

        assert session.headers["Authorization"] == "CustomScheme custom-token"

    def test_session_constructor_with_auth(self):
        """Test Session constructor with auth parameter."""
        auth = BearerAuth("constructor-token")
        session = Session(auth=auth)

        assert session.headers["Authorization"] == "Bearer constructor-token"

    def test_session_dict_auth_bearer(self):
        """Test Session with dict-based bearer auth (backward compatibility)."""
        session = Session()
        session.set_auth({"type": "bearer", "token": "dict-token"})

        assert session.headers["Authorization"] == "Bearer dict-token"

    def test_session_dict_auth_basic(self):
        """Test Session with dict-based basic auth (backward compatibility)."""
        session = Session()
        session.set_auth({"type": "basic", "username": "user", "password": "pass"})

        assert "Authorization" in session.headers
        assert session.headers["Authorization"].startswith("Basic ")

    def test_auth_replacement(self):
        """Test replacing authentication method."""
        session = Session()

        # Set initial auth
        session.set_auth(BearerAuth("token1"))
        assert session.headers["Authorization"] == "Bearer token1"

        # Replace with different auth
        session.set_auth(TokenAuth("token2", scheme="JWT"))
        assert session.headers["Authorization"] == "JWT token2"

    def test_custom_auth_class(self):
        """Test custom auth class with apply() method."""

        class CustomAuth:
            def apply(self, session):
                session.set_default_header("X-Custom-Auth", "custom-value")

        session = Session()
        auth = CustomAuth()
        session.set_auth(auth)

        assert session.headers["X-Custom-Auth"] == "custom-value"
