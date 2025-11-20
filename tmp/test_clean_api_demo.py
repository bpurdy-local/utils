from datetime import datetime

from pydantic import BaseModel

from utils import Index, JsonDB


class User(BaseModel):
    id: str = Index()
    name: str
    email: str
    created_at: datetime


def main():
    db = JsonDB(base_path="./tmp/clean_api_db")

    print("=== Clean JsonDB API ===\n")

    print("1. Save with explicit ID:")
    user1 = User(
        id="user-001", name="Alice", email="alice@example.com", created_at=datetime.now()
    )
    key = db.save(user1)
    print(f"   Saved: {key}\n")

    print("2. Save with auto-generated ID:")
    user2 = User(name="Bob", email="bob@example.com", created_at=datetime.now())
    key = db.save(user2)
    print(f"   Auto-generated: {key}")
    print(f"   user2.id is now: {user2.id}\n")

    print("3. Load by instance (no key needed!):")
    loaded = db.load(user1)
    print(f"   Loaded: {loaded.name} ({loaded.email})\n")

    print("4. Load by class + key:")
    loaded = db.load(User, key="user-001")
    print(f"   Loaded: {loaded.name}\n")

    print("5. Update by instance (no key needed!):")
    user1.name = "Alice Updated"
    db.update(user1)
    reloaded = db.load(user1)
    print(f"   Updated name: {reloaded.name}\n")

    print("6. Check existence by instance:")
    exists = db.exists(user1)
    print(f"   User exists: {exists}\n")

    print("7. Check existence by class + key:")
    exists = db.exists(User, key=user2.id)
    print(f"   User exists: {exists}\n")

    print("8. Delete by instance (no key needed!):")
    deleted = db.delete(user2)
    print(f"   Deleted: {deleted}\n")

    print("9. List all keys:")
    keys = db.list_keys(User)
    print(f"   All user keys: {keys}\n")

    print("10. Load all users:")
    all_users = db.load_all(User)
    for key, user in all_users.items():
        print(f"   {key}: {user.name} ({user.email})")

    print("\n=== File Structure ===")
    print("./tmp/clean_api_db/")
    print("  User/")
    for key in db.list_keys(User):
        print(f"    {key}.json")


if __name__ == "__main__":
    main()
