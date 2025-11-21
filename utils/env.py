import os
from pathlib import Path


class Env:
    """Environment variable utilities with type conversion and .env file loading."""

    @staticmethod
    def get(key: str, *, default: str | None = None, required: bool = False) -> str | None:
        """Get environment variable as string.

        Example: Env.get("DATABASE_URL", default="localhost")
        """
        value = os.environ.get(key)

        if value is None:
            if required:
                raise ValueError(f"Environment variable '{key}' is required but not set")
            return default

        return value

    @staticmethod
    def get_int(key: str, *, default: int | None = None, required: bool = False) -> int | None:
        """Get environment variable as integer.

        Example: Env.get_int("PORT", default=8000)
        """
        value = Env.get(key, required=required)

        if value is None:
            return default

        try:
            return int(value)
        except ValueError:
            raise ValueError(
                f"Environment variable '{key}' has value '{value}' which is not a valid integer"
            )

    @staticmethod
    def get_float(
        key: str, *, default: float | None = None, required: bool = False
    ) -> float | None:
        """Get environment variable as float.

        Example: Env.get_float("RATE_LIMIT", default=0.5)
        """
        value = Env.get(key, required=required)

        if value is None:
            return default

        try:
            return float(value)
        except ValueError:
            raise ValueError(
                f"Environment variable '{key}' has value '{value}' which is not a valid float"
            )

    @staticmethod
    def get_bool(key: str, *, default: bool = False, required: bool = False) -> bool:
        """Get environment variable as boolean.

        Accepts: true/false, 1/0, yes/no, on/off, t/f, y/n (case-insensitive)
        Example: Env.get_bool("DEBUG", default=False)
        """
        value = Env.get(key, required=required)

        if value is None:
            return default

        value_lower = value.lower()
        if value_lower in ("true", "1", "yes", "on", "t", "y"):
            return True
        if value_lower in ("false", "0", "no", "off", "f", "n", ""):
            return False

        raise ValueError(
            f"Environment variable '{key}' has value '{value}' which is not a valid boolean. "
            f"Valid values: true/false, 1/0, yes/no, on/off, t/f, y/n"
        )

    @staticmethod
    def get_list(
        key: str, *, separator: str = ",", default: list[str] | None = None, required: bool = False
    ) -> list[str]:
        """Get environment variable as list by splitting on separator.

        Example: Env.get_list("ALLOWED_HOSTS")  # "a,b,c" -> ["a", "b", "c"]
        """
        value = Env.get(key, required=required)

        if value is None:
            return default if default is not None else []

        if not value.strip():
            return []

        # Split on separator and strip whitespace from each item
        return [item.strip() for item in value.split(separator) if item.strip()]

    @staticmethod
    def get_path(
        key: str, *, default: Path | str | None = None, required: bool = False
    ) -> Path | None:
        """Get environment variable as Path object.

        Example: Env.get_path("DATA_DIR", default="/tmp/data")
        """
        value = Env.get(key, required=required)

        if value is None:
            return Path(default) if default is not None else None

        return Path(value)

    @staticmethod
    def set(key: str, value: str) -> None:
        """Set environment variable.

        Example: Env.set("API_KEY", "secret")
        """
        os.environ[key] = value

    @staticmethod
    def unset(key: str) -> None:
        """Remove environment variable if it exists.

        Example: Env.unset("TEMP_VAR")
        """
        os.environ.pop(key, None)

    @staticmethod
    def has(key: str) -> bool:
        """Check if environment variable exists.

        Example: Env.has("PATH")  # True
        """
        return key in os.environ

    @staticmethod
    def load_dotenv(*, path: str | Path = ".env", override: bool = False) -> dict[str, str]:
        """Load environment variables from .env file.

        Supports quoted values, comments, and escape sequences.
        Example: Env.load_dotenv(path=".env.local", override=True)
        """
        env_path = Path(path)

        if not env_path.exists():
            return {}

        loaded = {}
        with open(env_path, encoding="utf-8") as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()

                # Skip empty lines and comments
                if not line or line.startswith("#"):
                    continue

                if "=" not in line:
                    continue

                # Parse key=value
                key, _, value = line.partition("=")
                key = key.strip()
                value = value.strip()

                # Remove quotes if present
                if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
                    value = value[1:-1]

                # Process escape sequences
                value = value.replace("\\n", "\n").replace("\\t", "\t")

                # Only set if override=True or variable doesn't exist
                if override or key not in os.environ:
                    os.environ[key] = value
                    loaded[key] = value

        return loaded

    @staticmethod
    def to_dict() -> dict[str, str]:
        """Get all environment variables as dictionary.

        Example: Env.to_dict()
        """
        return dict(os.environ)

    @staticmethod
    def clear() -> None:
        """Clear all environment variables.

        Example: Env.clear()  # Use with caution!
        """
        os.environ.clear()

    @staticmethod
    def get_with_prefix(prefix: str) -> dict[str, str]:
        """Get all environment variables that start with prefix.

        Example: Env.get_with_prefix("AWS_")  # {"AWS_REGION": "us-east-1", ...}
        """
        return {key: value for key, value in os.environ.items() if key.startswith(prefix)}

    @staticmethod
    def require(*keys: str) -> None:
        """Validate that required environment variables are set.

        Raises ValueError if any are missing.
        Example: Env.require("DATABASE_URL", "SECRET_KEY")
        """
        missing = [key for key in keys if key not in os.environ]

        if missing:
            raise ValueError(f"Required environment variables are missing: {', '.join(missing)}")
