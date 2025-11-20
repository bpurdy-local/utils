import json
import tempfile
from datetime import datetime
from pathlib import Path

import pytest
from pydantic import BaseModel

from utils.db.json import Index, JsonDB


class User(BaseModel):
    id: str = Index()
    name: str
    email: str
    age: int


class Post(BaseModel):
    id: str = Index()
    title: str
    content: str
    created_at: datetime


class Profile(BaseModel):
    id: str = Index()
    bio: str
    tags: list[str]
    metadata: dict[str, str]


@pytest.fixture
def temp_db():
    with tempfile.TemporaryDirectory() as tmpdir:
        yield JsonDB(base_path=tmpdir)


@pytest.fixture
def sample_user():
    return User(id="123", name="Alice", email="alice@example.com", age=30)


@pytest.fixture
def sample_post():
    return Post(
        id="post1",
        title="Test Post",
        content="This is a test post",
        created_at=datetime(2025, 1, 15, 12, 0, 0),
    )


@pytest.fixture
def sample_profile():
    return Profile(
        id="prof1",
        bio="Software developer",
        tags=["python", "testing", "pydantic"],
        metadata={"location": "NYC", "company": "Tech Corp"},
    )


class TestJsonDBBasicOperations:
    def test_save_and_load(self, temp_db, sample_user):
        temp_db.save(sample_user)
        loaded = temp_db.load(User, key="123")

        assert loaded is not None
        assert loaded.id == sample_user.id
        assert loaded.name == sample_user.name
        assert loaded.email == sample_user.email
        assert loaded.age == sample_user.age

    def test_load_by_instance(self, temp_db, sample_user):
        temp_db.save(sample_user)
        loaded = temp_db.load(sample_user)

        assert loaded is not None
        assert loaded.name == sample_user.name

    def test_load_nonexistent(self, temp_db):
        loaded = temp_db.load(User, key="nonexistent")
        assert loaded is None

    def test_save_creates_directory(self, temp_db, sample_user):
        temp_db.save(sample_user)
        model_dir = temp_db.base_path / "User"
        assert model_dir.exists()
        assert model_dir.is_dir()

    def test_save_creates_json_file(self, temp_db, sample_user):
        temp_db.save(sample_user)
        file_path = temp_db.base_path / "User" / "123.json"
        assert file_path.exists()
        assert file_path.is_file()

    def test_delete_existing(self, temp_db, sample_user):
        temp_db.save(sample_user)
        result = temp_db.delete(sample_user)

        assert result is True
        assert not temp_db.exists(sample_user)

    def test_delete_by_class_and_key(self, temp_db, sample_user):
        temp_db.save(sample_user)
        result = temp_db.delete(User, key="123")

        assert result is True
        assert not temp_db.exists(User, key="123")

    def test_delete_nonexistent(self, temp_db):
        result = temp_db.delete(User, key="nonexistent")
        assert result is False

    def test_exists_true(self, temp_db, sample_user):
        temp_db.save(sample_user)
        assert temp_db.exists(sample_user) is True

    def test_exists_by_class_and_key(self, temp_db, sample_user):
        temp_db.save(sample_user)
        assert temp_db.exists(User, key="123") is True

    def test_exists_false(self, temp_db):
        assert temp_db.exists(User, key="nonexistent") is False

    def test_update_existing(self, temp_db, sample_user):
        temp_db.save(sample_user)

        sample_user.name = "Bob"
        sample_user.age = 31
        existed = temp_db.update(sample_user)

        assert existed is True
        loaded = temp_db.load(sample_user)
        assert loaded is not None
        assert loaded.name == "Bob"
        assert loaded.age == 31

    def test_update_new(self, temp_db, sample_user):
        existed = temp_db.update(sample_user)

        assert existed is False
        assert temp_db.exists(sample_user) is True


class TestJsonDBMultipleModels:
    def test_different_model_classes(self, temp_db, sample_user, sample_post):
        temp_db.save(sample_user)
        temp_db.save(sample_post)

        loaded_user = temp_db.load(sample_user)
        loaded_post = temp_db.load(sample_post)

        assert loaded_user is not None
        assert loaded_post is not None
        assert loaded_user.name == "Alice"
        assert loaded_post.title == "Test Post"

    def test_same_key_different_models(self, temp_db):
        user = User(id="1", name="Alice", email="alice@example.com", age=30)
        post = Post(
            id="1",
            title="Post",
            content="Content",
            created_at=datetime(2025, 1, 15, 12, 0, 0),
        )

        temp_db.save(user)
        temp_db.save(post)

        loaded_user = temp_db.load(User, key="1")
        loaded_post = temp_db.load(Post, key="1")

        assert loaded_user is not None
        assert loaded_post is not None
        assert loaded_user.email == "alice@example.com"
        assert loaded_post.title == "Post"

    def test_list_keys_single_model(self, temp_db):
        user1 = User(id="1", name="Alice", email="alice@example.com", age=30)
        user2 = User(id="2", name="Bob", email="bob@example.com", age=25)
        user3 = User(id="3", name="Charlie", email="charlie@example.com", age=35)

        temp_db.save(user1)
        temp_db.save(user2)
        temp_db.save(user3)

        keys = temp_db.list_keys(User)
        assert set(keys) == {"1", "2", "3"}

    def test_list_keys_empty(self, temp_db):
        keys = temp_db.list_keys(User)
        assert keys == []

    def test_list_keys_multiple_models(self, temp_db, sample_user, sample_post):
        temp_db.save(sample_user)
        temp_db.save(sample_post)

        user_keys = temp_db.list_keys(User)
        post_keys = temp_db.list_keys(Post)

        assert user_keys == ["123"]
        assert post_keys == ["post1"]

    def test_load_all(self, temp_db):
        user1 = User(id="1", name="Alice", email="alice@example.com", age=30)
        user2 = User(id="2", name="Bob", email="bob@example.com", age=25)

        temp_db.save(user1)
        temp_db.save(user2)

        all_users = temp_db.load_all(User)
        assert len(all_users) == 2
        assert "1" in all_users
        assert "2" in all_users
        assert all_users["1"].name == "Alice"
        assert all_users["2"].name == "Bob"

    def test_load_all_empty(self, temp_db):
        all_users = temp_db.load_all(User)
        assert all_users == {}

    def test_clear(self, temp_db):
        user1 = User(id="1", name="Alice", email="alice@example.com", age=30)
        user2 = User(id="2", name="Bob", email="bob@example.com", age=25)
        post = Post(
            id="p1",
            title="Test",
            content="Content",
            created_at=datetime(2025, 1, 15, 12, 0, 0),
        )

        temp_db.save(user1)
        temp_db.save(user2)
        temp_db.save(post)

        deleted = temp_db.clear(User)

        assert deleted == 2
        assert temp_db.list_keys(User) == []
        assert temp_db.list_keys(Post) == ["p1"]

    def test_clear_empty(self, temp_db):
        deleted = temp_db.clear(User)
        assert deleted == 0


class TestJsonDBNestedData:
    def test_nested_lists(self, temp_db, sample_profile):
        temp_db.save(sample_profile)
        loaded = temp_db.load(sample_profile)

        assert loaded is not None
        assert loaded.tags == ["python", "testing", "pydantic"]

    def test_nested_dicts(self, temp_db, sample_profile):
        temp_db.save(sample_profile)
        loaded = temp_db.load(sample_profile)

        assert loaded is not None
        assert loaded.metadata == {"location": "NYC", "company": "Tech Corp"}

    def test_datetime_serialization(self, temp_db, sample_post):
        temp_db.save(sample_post)
        loaded = temp_db.load(sample_post)

        assert loaded is not None
        assert loaded.created_at == datetime(2025, 1, 15, 12, 0, 0)

    def test_json_file_structure(self, temp_db, sample_profile):
        temp_db.save(sample_profile)
        file_path = temp_db.base_path / "Profile" / "prof1.json"

        with open(file_path, encoding="utf-8") as f:
            data = json.load(f)

        assert data["id"] == "prof1"
        assert data["bio"] == "Software developer"
        assert data["tags"] == ["python", "testing", "pydantic"]
        assert data["metadata"] == {"location": "NYC", "company": "Tech Corp"}


class TestJsonDBPathHandling:
    def test_custom_base_path(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            custom_path = Path(tmpdir) / "custom" / "db"
            db = JsonDB(base_path=custom_path)

            assert db.base_path == custom_path
            assert custom_path.exists()

    def test_string_base_path(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db = JsonDB(base_path=tmpdir)
            assert isinstance(db.base_path, Path)

    def test_model_directory_structure(self, temp_db, sample_user, sample_post):
        temp_db.save(sample_user)
        temp_db.save(sample_post)

        user_dir = temp_db.base_path / "User"
        post_dir = temp_db.base_path / "Post"

        assert user_dir.exists()
        assert post_dir.exists()
        assert (user_dir / "123.json").exists()
        assert (post_dir / "post1.json").exists()

    def test_special_characters_in_key(self, temp_db):
        user = User(id="user_123-abc", name="Test", email="test@example.com", age=25)
        temp_db.save(user)
        loaded = temp_db.load(user)

        assert loaded is not None
        assert loaded.id == "user_123-abc"


class TestJsonDBEdgeCases:
    def test_overwrite_existing(self, temp_db):
        user1 = User(id="user", name="Alice", email="alice@example.com", age=30)
        user2 = User(id="user", name="Bob", email="bob@example.com", age=25)

        temp_db.save(user1)
        temp_db.save(user2)

        loaded = temp_db.load(User, key="user")
        assert loaded is not None
        assert loaded.name == "Bob"

    def test_unicode_content(self, temp_db):
        user = User(id="1", name="Alice 你好", email="alice@例え.com", age=30)
        temp_db.save(user)
        loaded = temp_db.load(user)

        assert loaded is not None
        assert loaded.name == "Alice 你好"
        assert loaded.email == "alice@例え.com"

    def test_large_model(self, temp_db):
        class LargeModel(BaseModel):
            id: str = Index()
            data: list[int]

        large_data = list(range(10000))
        model = LargeModel(id="large", data=large_data)

        temp_db.save(model)
        loaded = temp_db.load(model)

        assert loaded is not None
        assert loaded.data == large_data


class TestJsonDBIndexField:
    def test_model_with_index_field(self, temp_db):
        user = User(id="user-123", name="Alice", email="alice@example.com", age=30)
        key = temp_db.save(user)

        assert key == "user-123"
        assert temp_db.exists(User, key="user-123")

    def test_auto_generate_index_when_empty(self, temp_db):
        user = User(name="Bob", email="bob@example.com", age=25)
        key = temp_db.save(user)

        assert key is not None
        assert len(key) == 36
        assert user.id == key
        assert temp_db.exists(User, key=key)

    def test_load_by_model_instance(self, temp_db):
        user = User(id="user-456", name="Charlie", email="charlie@example.com", age=28)
        temp_db.save(user)

        loaded = temp_db.load(user)
        assert loaded is not None
        assert loaded.name == "Charlie"
        assert loaded.id == "user-456"

    def test_load_by_class_and_key(self, temp_db):
        user = User(id="user-789", name="Diana", email="diana@example.com", age=32)
        temp_db.save(user)

        loaded = temp_db.load(User, key="user-789")
        assert loaded is not None
        assert loaded.name == "Diana"

    def test_delete_by_model_instance(self, temp_db):
        user = User(id="user-delete", name="Eve", email="eve@example.com", age=27)
        temp_db.save(user)

        deleted = temp_db.delete(user)
        assert deleted is True
        assert not temp_db.exists(User, key="user-delete")

    def test_delete_by_class_and_key(self, temp_db):
        user = User(id="user-delete2", name="Frank", email="frank@example.com", age=29)
        temp_db.save(user)

        deleted = temp_db.delete(User, key="user-delete2")
        assert deleted is True

    def test_exists_by_model_instance(self, temp_db):
        user = User(id="user-exists", name="Grace", email="grace@example.com", age=31)
        temp_db.save(user)

        assert temp_db.exists(user) is True

    def test_exists_by_class_and_key(self, temp_db):
        user = User(id="user-exists2", name="Henry", email="henry@example.com", age=33)
        temp_db.save(user)

        assert temp_db.exists(User, key="user-exists2") is True

    def test_update_with_index_field(self, temp_db):
        user = User(id="user-update", name="Ivy", email="ivy@example.com", age=26)
        existed = temp_db.update(user)

        assert existed is False
        assert temp_db.exists(user)

        user.name = "Ivy Updated"
        existed = temp_db.update(user)

        assert existed is True
        loaded = temp_db.load(user)
        assert loaded.name == "Ivy Updated"

    def test_multiple_index_fields_uses_first(self, temp_db):
        class MultiIndex(BaseModel):
            id1: str = Index()
            id2: str = Index()
            name: str

        model = MultiIndex(id1="first", id2="second", name="Test")
        key = temp_db.save(model)

        assert key == "first"

    def test_index_field_persisted_in_json(self, temp_db):
        user = User(id="persist-test", name="Karen", email="karen@example.com", age=34)
        temp_db.save(user)

        file_path = temp_db.base_path / "User" / "persist-test.json"
        with open(file_path, encoding="utf-8") as f:
            data = json.load(f)

        assert data["id"] == "persist-test"
        assert data["name"] == "Karen"

    def test_model_without_index_raises_error(self, temp_db):
        class NoIndex(BaseModel):
            name: str

        model = NoIndex(name="Test")

        with pytest.raises(ValueError, match="does not have an Index field"):
            temp_db.save(model)

    def test_load_without_key_raises_error(self, temp_db):
        with pytest.raises(ValueError, match="must provide a key parameter"):
            temp_db.load(User)

    def test_delete_without_key_raises_error(self, temp_db):
        with pytest.raises(ValueError, match="must provide a key parameter"):
            temp_db.delete(User)

    def test_exists_without_key_raises_error(self, temp_db):
        with pytest.raises(ValueError, match="must provide a key parameter"):
            temp_db.exists(User)

    def test_load_instance_without_index_value_raises_error(self, temp_db):
        user = User(name="No ID", email="test@example.com", age=25)

        with pytest.raises(ValueError, match="is empty"):
            temp_db.load(user)
