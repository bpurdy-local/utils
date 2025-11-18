"""Authentication classes for HTTP sessions."""

import base64
from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from utils.session.session import Session


class Auth(Protocol):
    """Protocol for authentication objects."""

    def apply(self, session: "Session") -> None:
        """Apply authentication to the session.

        Args:
            session: Session instance to configure
        """
        ...


class BearerAuth:
    """Bearer token authentication."""

    def __init__(self, token: str):
        """Initialize with bearer token.

        Args:
            token: Bearer token string
        """
        self.token = token

    def apply(self, session: "Session") -> None:
        """Apply bearer token to session headers.

        Args:
            session: Session instance to configure
        """
        session.set_default_header("Authorization", f"Bearer {self.token}")


class BasicAuth:
    """HTTP Basic authentication."""

    def __init__(self, username: str, password: str):
        """Initialize with username and password.

        Args:
            username: Username for basic auth
            password: Password for basic auth
        """
        self.username = username
        self.password = password

    def apply(self, session: "Session") -> None:
        """Apply basic auth to session headers.

        Args:
            session: Session instance to configure
        """
        credentials = f"{self.username}:{self.password}".encode()
        encoded_credentials = base64.b64encode(credentials).decode("ascii")
        session.set_default_header("Authorization", f"Basic {encoded_credentials}")


class APIKeyAuth:
    """API key authentication (custom header)."""

    def __init__(self, api_key: str, *, header_name: str = "X-API-Key"):
        """Initialize with API key and optional header name.

        Args:
            api_key: API key string
            header_name: Name of header to use (default: "X-API-Key")
        """
        self.api_key = api_key
        self.header_name = header_name

    def apply(self, session: "Session") -> None:
        """Apply API key to session headers.

        Args:
            session: Session instance to configure
        """
        session.set_default_header(self.header_name, self.api_key)


class TokenAuth:
    """Generic token authentication with custom scheme."""

    def __init__(self, token: str, *, scheme: str = "Token"):
        """Initialize with token and scheme.

        Args:
            token: Token string
            scheme: Authorization scheme (default: "Token")
        """
        self.token = token
        self.scheme = scheme

    def apply(self, session: "Session") -> None:
        """Apply token to session headers.

        Args:
            session: Session instance to configure
        """
        session.set_default_header("Authorization", f"{self.scheme} {self.token}")
