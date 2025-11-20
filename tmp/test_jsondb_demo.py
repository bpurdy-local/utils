"""Demo script for JsonDB functionality."""

from datetime import datetime

from pydantic import BaseModel

from utils import JsonDB


# Define Pydantic models
class User(BaseModel):
    """User model."""

    id: str
    name: str
    email: str
    age: int


class Post(BaseModel):
    """Post model with nested data."""

    id: str
    title: str
    content: str
    tags: list[str]
    created_at: datetime


def main():
    """Demonstrate JsonDB functionality."""
    # Create a database instance
    db = JsonDB(base_path="./tmp/demo_db")

    # Create and save users
    users = [
        User(id="1", name="Alice", email="alice@example.com", age=30),
        User(id="2", name="Bob", email="bob@example.com", age=25),
        User(id="3", name="Charlie", email="charlie@example.com", age=35),
    ]

    print("Saving users...")
    for user in users:
        db.save(user, key=user.id)
        print(f"  Saved: {user.name}")

    # Load and display a user
    print("\nLoading user 1...")
    loaded_user = db.load(User, key="1")
    if loaded_user:
        print(f"  Loaded: {loaded_user.name}, age {loaded_user.age}")

    # List all user keys
    print("\nListing all user keys...")
    user_keys = db.list_keys(User)
    print(f"  Keys: {user_keys}")

    # Load all users
    print("\nLoading all users...")
    all_users = db.load_all(User)
    for key, user in all_users.items():
        print(f"  {key}: {user.name} ({user.email})")

    # Create and save posts
    posts = [
        Post(
            id="p1",
            title="Introduction to Python",
            content="Python is awesome!",
            tags=["python", "programming"],
            created_at=datetime.now(),
        ),
        Post(
            id="p2",
            title="Database Design",
            content="Best practices for databases",
            tags=["database", "design"],
            created_at=datetime.now(),
        ),
    ]

    print("\nSaving posts...")
    for post in posts:
        db.save(post, key=post.id)
        print(f"  Saved: {post.title}")

    # Update a user
    print("\nUpdating user 1...")
    if loaded_user:
        loaded_user.age = 31
        db.update(loaded_user, key="1")
        print(f"  Updated age to {loaded_user.age}")

    # Verify update
    updated_user = db.load(User, key="1")
    if updated_user:
        print(f"  Verified: {updated_user.name} is now {updated_user.age} years old")

    # Check existence
    print("\nChecking existence...")
    print(f"  User 1 exists: {db.exists(User, key='1')}")
    print(f"  User 999 exists: {db.exists(User, key='999')}")

    # Display directory structure
    print("\nDatabase structure:")
    print("  ./tmp/demo_db/")
    print("    User/")
    for key in db.list_keys(User):
        print(f"      {key}.json")
    print("    Post/")
    for key in db.list_keys(Post):
        print(f"      {key}.json")

    # Clean up - delete one user
    print("\nDeleting user 2...")
    deleted = db.delete(User, key="2")
    print(f"  Deleted: {deleted}")
    print(f"  Remaining users: {db.list_keys(User)}")

    # Clear all posts
    print("\nClearing all posts...")
    deleted_count = db.clear(Post)
    print(f"  Deleted {deleted_count} posts")
    print(f"  Remaining posts: {db.list_keys(Post)}")


if __name__ == "__main__":
    main()
