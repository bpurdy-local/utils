import contextlib
import fcntl
import json
import os
import tempfile
import uuid
from pathlib import Path
from typing import TypeVar, overload

from pydantic import BaseModel, Field

from utils.json_encoder import JsonEncoder

T = TypeVar("T", bound=BaseModel)


def Index() -> str:
    return Field(default="", json_schema_extra={"is_index": True})


class JsonDB:
    def __init__(self, base_path: str | Path = "./data"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)

    @contextlib.contextmanager
    def _lock_file(self, file_path: Path, *, exclusive: bool = False):
        lock_path = Path(f"{file_path}.lock")
        lock_mode = fcntl.LOCK_EX if exclusive else fcntl.LOCK_SH

        lock_path.parent.mkdir(parents=True, exist_ok=True)
        lock_file = open(lock_path, "w", encoding="utf-8")

        try:
            fcntl.flock(lock_file.fileno(), lock_mode)
            yield lock_file
        finally:
            fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)
            lock_file.close()
            try:
                lock_path.unlink()
            except FileNotFoundError:
                pass

    @staticmethod
    def _get_index_field(model_class: type[BaseModel]) -> str | None:
        try:
            fields = model_class.model_fields
        except AttributeError:
            fields = model_class.__fields__

        for field_name, field_info in fields.items():
            try:
                if field_info.json_schema_extra and field_info.json_schema_extra.get("is_index"):
                    return field_name
            except (AttributeError, TypeError):
                pass

        return None

    @staticmethod
    def _get_index_value(model: BaseModel) -> str:
        index_field = JsonDB._get_index_field(type(model))
        if not index_field:
            raise ValueError(
                f"{type(model).__name__} does not have an Index field. "
                f"Mark a field with Index() to use JsonDB."
            )

        value = getattr(model, index_field, None)
        if not value:
            raise ValueError(
                f"{type(model).__name__}.{index_field} is empty. "
                f"Index field must have a value or be auto-generated via save()."
            )
        return value

    @staticmethod
    def _set_index_value(model: BaseModel, *, value: str) -> None:
        index_field = JsonDB._get_index_field(type(model))
        if not index_field:
            raise ValueError(
                f"{type(model).__name__} does not have an Index field. "
                f"Mark a field with Index() to use JsonDB."
            )
        setattr(model, index_field, value)

    def _get_model_dir(self, model_class: type[BaseModel]) -> Path:
        model_dir = self.base_path / model_class.__name__
        model_dir.mkdir(parents=True, exist_ok=True)
        return model_dir

    def _get_file_path(self, model_class: type[BaseModel], key: str) -> Path:
        model_dir = self._get_model_dir(model_class)
        return model_dir / f"{key}.json"

    def save(self, model: BaseModel) -> str:
        index_field = self._get_index_field(type(model))
        if not index_field:
            raise ValueError(
                f"{type(model).__name__} does not have an Index field. "
                f"Mark a field with Index() to use JsonDB."
            )

        key = getattr(model, index_field, None)
        if not key:
            key = str(uuid.uuid4())
            self._set_index_value(model, value=key)

        file_path = self._get_file_path(type(model), key)

        try:
            data = model.model_dump()
        except AttributeError:
            data = model.dict()

        with self._lock_file(file_path, exclusive=True):
            model_dir = file_path.parent
            fd, temp_path = tempfile.mkstemp(dir=model_dir, suffix=".json.tmp", text=True)

            try:
                with os.fdopen(fd, "w", encoding="utf-8") as f:
                    json.dump(data, f, cls=JsonEncoder, indent=2, ensure_ascii=False)
                    f.flush()
                    os.fsync(f.fileno())

                os.replace(temp_path, file_path)
            except Exception:
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
                raise

        return key

    @overload
    def load(self, model_or_class: type[T], *, key: str) -> T | None: ...

    @overload
    def load(self, model_or_class: T) -> T | None: ...

    def load(self, model_or_class: BaseModel | type[T], *, key: str | None = None) -> T | None:
        if isinstance(model_or_class, type):
            if key is None:
                raise ValueError(
                    f"When loading by class, you must provide a key parameter. "
                    f"Use db.load({model_or_class.__name__}, key='...')"
                )
            model_class = model_or_class
        else:
            model_class = type(model_or_class)
            key = self._get_index_value(model_or_class)

        file_path = self._get_file_path(model_class, key)

        if not file_path.exists():
            return None

        with self._lock_file(file_path, exclusive=False):
            with open(file_path, encoding="utf-8") as f:
                data = json.load(f)

        try:
            return model_class.model_validate(data)
        except AttributeError:
            return model_class.parse_obj(data)

    @overload
    def delete(self, model_or_class: type[BaseModel], *, key: str) -> bool: ...

    @overload
    def delete(self, model_or_class: BaseModel) -> bool: ...

    def delete(
        self, model_or_class: BaseModel | type[BaseModel], *, key: str | None = None
    ) -> bool:
        if isinstance(model_or_class, type):
            if key is None:
                raise ValueError(
                    f"When deleting by class, you must provide a key parameter. "
                    f"Use db.delete({model_or_class.__name__}, key='...')"
                )
            model_class = model_or_class
        else:
            model_class = type(model_or_class)
            key = self._get_index_value(model_or_class)

        file_path = self._get_file_path(model_class, key)

        if not file_path.exists():
            return False

        with self._lock_file(file_path, exclusive=True):
            if file_path.exists():
                file_path.unlink()
                return True
            return False

    @overload
    def exists(self, model_or_class: type[BaseModel], *, key: str) -> bool: ...

    @overload
    def exists(self, model_or_class: BaseModel) -> bool: ...

    def exists(
        self, model_or_class: BaseModel | type[BaseModel], *, key: str | None = None
    ) -> bool:
        if isinstance(model_or_class, type):
            if key is None:
                raise ValueError(
                    f"When checking existence by class, you must provide a key parameter. "
                    f"Use db.exists({model_or_class.__name__}, key='...')"
                )
            model_class = model_or_class
        else:
            model_class = type(model_or_class)
            key = self._get_index_value(model_or_class)

        file_path = self._get_file_path(model_class, key)
        return file_path.exists()

    def list_keys(self, model_class: type[BaseModel]) -> list[str]:
        model_dir = self._get_model_dir(model_class)

        if not model_dir.exists():
            return []

        return [f.stem for f in model_dir.glob("*.json")]

    def load_all(self, model_class: type[T]) -> dict[str, T]:
        keys = self.list_keys(model_class)
        result: dict[str, T] = {}

        for key in keys:
            model = self.load(model_class, key=key)
            if model is not None:
                result[key] = model

        return result

    def clear(self, model_class: type[BaseModel]) -> int:
        keys = self.list_keys(model_class)
        deleted = 0

        for key in keys:
            if self.delete(model_class, key=key):
                deleted += 1

        return deleted

    def update(self, model: BaseModel) -> bool:
        index_field = self._get_index_field(type(model))
        if not index_field:
            raise ValueError(
                f"{type(model).__name__} does not have an Index field. "
                f"Mark a field with Index() to use JsonDB."
            )

        key = getattr(model, index_field, None)
        if not key:
            key = str(uuid.uuid4())
            self._set_index_value(model, value=key)

        existed = self.exists(model)
        self.save(model)
        return existed
