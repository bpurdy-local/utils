from datetime import datetime

from pydantic import BaseModel

from utils import Index, JsonDB


class UserWithIndex(BaseModel):
    id: str = Index()
    name: str
    email: str
    created_at: datetime


class ProductWithoutIndex(BaseModel):
    name: str
    price: float


def main():
    db = JsonDB(base_path="./tmp/index_demo_db")

    print("=== Testing Index Field ===\n")

    print("1. Save with explicit index:")
    user1 = UserWithIndex(
        id="user-001", name="Alice", email="alice@example.com", created_at=datetime.now()
    )
    key = db.save(user1)
    print(f"   Saved with key: {key}")
    print(f"   File: UserWithIndex/{key}.json\n")

    print("2. Save with auto-generated index:")
    user2 = UserWithIndex(name="Bob", email="bob@example.com", created_at=datetime.now())
    key = db.save(user2)
    print(f"   Auto-generated key: {key}")
    print(f"   User id field set to: {user2.id}\n")

    print("3. Load by model instance (using index field):")
    loaded = db.load(user1)
    print(f"   Loaded: {loaded.name} ({loaded.email})\n")

    print("4. Load by class and key:")
    loaded = db.load(UserWithIndex, key="user-001")
    print(f"   Loaded: {loaded.name} ({loaded.email})\n")

    print("5. Check existence using model instance:")
    exists = db.exists(user1)
    print(f"   User 'user-001' exists: {exists}\n")

    print("6. Delete using model instance:")
    deleted = db.delete(user2)
    print(f"   Deleted user with id '{user2.id}': {deleted}\n")

    print("7. Update using index field:")
    user1.name = "Alice Updated"
    existed = db.update(user1)
    print(f"   Updated (existed before): {existed}")
    reloaded = db.load(user1)
    print(f"   New name: {reloaded.name}\n")

    print("=== Backward Compatibility (models without Index) ===\n")

    print("8. Save model without Index field (manual key):")
    product = ProductWithoutIndex(name="Widget", price=19.99)
    key = db.save(product, key="widget-001")
    print(f"   Saved with key: {key}")
    print(f"   File: ProductWithoutIndex/{key}.json\n")

    print("9. Load model without Index field:")
    loaded_product = db.load(ProductWithoutIndex, key="widget-001")
    print(f"   Loaded: {loaded_product.name} - ${loaded_product.price}\n")

    print("=== File Structure ===")
    print("./tmp/index_demo_db/")
    print("  UserWithIndex/")
    for key in db.list_keys(UserWithIndex):
        print(f"    {key}.json")
    print("  ProductWithoutIndex/")
    for key in db.list_keys(ProductWithoutIndex):
        print(f"    {key}.json")


if __name__ == "__main__":
    main()
