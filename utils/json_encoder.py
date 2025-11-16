import datetime
import json
from typing import Any


class JsonEncoder(json.JSONEncoder):
    """Custom JSON encoder for common Python types (datetime, set, tuple, objects with to_dict)."""

    def default(self, obj: Any) -> Any:
        """Encode common Python types to JSON-serializable format."""
        if isinstance(obj, tuple):
            return list(obj)

        if isinstance(obj, set):
            return list(obj)

        # Handle arrow datetime if available
        try:
            import arrow

            if isinstance(obj, arrow.Arrow):
                return obj.isoformat()
        except ImportError:
            pass

        if isinstance(obj, datetime.datetime):
            return obj.isoformat()

        if isinstance(obj, datetime.date):
            return obj.isoformat()

        # Try to_dict method first, then fall back to __dict__
        if hasattr(obj, "to_dict") and callable(obj.to_dict):
            return obj.to_dict()

        if hasattr(obj, "__dict__"):
            return obj.__dict__

        return str(obj)
