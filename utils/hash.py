"""Hash utility class."""

import hashlib
import hmac
from pathlib import Path


class Hash:
    """Static utility class for hashing operations."""

    @staticmethod
    def md5(data: str | bytes) -> str:
        """Generate MD5 hash (not cryptographically secure, use for checksums only).

        Examples:
            >>> Hash.md5("hello")
            '5d41402abc4b2a76b9719d911017c592'
            >>> Hash.md5(b"hello")
            '5d41402abc4b2a76b9719d911017c592'
        """
        if isinstance(data, str):
            data = data.encode("utf-8")
        return hashlib.md5(data).hexdigest()

    @staticmethod
    def sha1(data: str | bytes) -> str:
        """Generate SHA-1 hash (not cryptographically secure for new applications).

        Examples:
            >>> Hash.sha1("hello")
            'aaf4c61ddcc5e8a2dabede0f3b482cd9aea9434d'
        """
        if isinstance(data, str):
            data = data.encode("utf-8")
        return hashlib.sha1(data).hexdigest()

    @staticmethod
    def sha256(data: str | bytes) -> str:
        """Generate SHA-256 hash (cryptographically secure).

        Examples:
            >>> Hash.sha256("hello")
            '2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824'
        """
        if isinstance(data, str):
            data = data.encode("utf-8")
        return hashlib.sha256(data).hexdigest()

    @staticmethod
    def sha512(data: str | bytes) -> str:
        """Generate SHA-512 hash (cryptographically secure).

        Examples:
            >>> Hash.sha512("hello")[:20]
            '9b71d224bd62f3785d'
        """
        if isinstance(data, str):
            data = data.encode("utf-8")
        return hashlib.sha512(data).hexdigest()

    @staticmethod
    def file(path: str | Path, *, algorithm: str = "sha256", chunk_size: int = 8192) -> str:
        """Generate hash of file contents.

        Examples:
            >>> # Assuming test file exists
            >>> hash_val = Hash.file("test.txt")
            >>> len(hash_val)
            64
            >>> Hash.file("test.txt", algorithm="md5")  # doctest: +SKIP
        """
        file_path = Path(path)

        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {path}")

        # Select hash algorithm
        if algorithm == "md5":
            hasher = hashlib.md5()
        elif algorithm == "sha1":
            hasher = hashlib.sha1()
        elif algorithm == "sha256":
            hasher = hashlib.sha256()
        elif algorithm == "sha512":
            hasher = hashlib.sha512()
        else:
            raise ValueError(f"Unsupported algorithm: {algorithm}")

        # Read file in chunks to handle large files
        with open(file_path, "rb") as f:
            while chunk := f.read(chunk_size):
                hasher.update(chunk)

        return hasher.hexdigest()

    @staticmethod
    def verify(data: str | bytes, hash_value: str, *, algorithm: str = "sha256") -> bool:
        """Verify data matches hash value using timing-safe comparison.

        Examples:
            >>> data = "hello"
            >>> hash_val = Hash.sha256(data)
            >>> Hash.verify(data, hash_val)
            True
            >>> Hash.verify(data, "wrong_hash")
            False
        """
        if algorithm == "md5":
            computed = Hash.md5(data)
        elif algorithm == "sha1":
            computed = Hash.sha1(data)
        elif algorithm == "sha256":
            computed = Hash.sha256(data)
        elif algorithm == "sha512":
            computed = Hash.sha512(data)
        else:
            raise ValueError(f"Unsupported algorithm: {algorithm}")

        # Timing-safe comparison
        return hmac.compare_digest(computed, hash_value)

    @staticmethod
    def hmac_sha256(data: str | bytes, key: str | bytes) -> str:
        """Generate HMAC-SHA256 for authenticated hashing.

        Examples:
            >>> Hash.hmac_sha256("message", "secret_key")
            '5d5d139563c95b5967b9bd9a8c9b233a9dedb45072794cd232dc1b74832607d0'
        """
        if isinstance(data, str):
            data = data.encode("utf-8")
        if isinstance(key, str):
            key = key.encode("utf-8")

        return hmac.new(key, data, hashlib.sha256).hexdigest()

    @staticmethod
    def hmac_verify(
        data: str | bytes, key: str | bytes, hash_value: str, *, algorithm: str = "sha256"
    ) -> bool:
        """Verify HMAC hash using timing-safe comparison.

        Examples:
            >>> data = "message"
            >>> key = "secret"
            >>> hash_val = Hash.hmac_sha256(data, key)
            >>> Hash.hmac_verify(data, key, hash_val)
            True
        """
        if isinstance(data, str):
            data = data.encode("utf-8")
        if isinstance(key, str):
            key = key.encode("utf-8")

        if algorithm == "sha256":
            hasher = hashlib.sha256
        elif algorithm == "sha1":
            hasher = hashlib.sha1
        elif algorithm == "sha512":
            hasher = hashlib.sha512
        elif algorithm == "md5":
            hasher = hashlib.md5
        else:
            raise ValueError(f"Unsupported algorithm: {algorithm}")

        computed = hmac.new(key, data, hasher).hexdigest()
        return hmac.compare_digest(computed, hash_value)

    @staticmethod
    def checksum(data: str | bytes) -> str:
        """Generate quick checksum for data integrity (uses MD5).

        Examples:
            >>> Hash.checksum("data")
            '8d777f385d3dfec8815d20f7496026dc'
        """
        return Hash.md5(data)
