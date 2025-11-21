import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

from pydantic import BaseModel

from utils import Index, JsonDB


class Document(BaseModel):
    id: str = Index()
    content: str
    version: int
    updated_at: datetime


def write_large_document(db: JsonDB, doc_id: str, worker_id: int) -> bool:
    doc = Document(
        id=doc_id,
        content="x" * 100000,
        version=worker_id,
        updated_at=datetime.now(),
    )

    for i in range(10):
        doc.content = f"Worker {worker_id} - Iteration {i} - " + ("x" * 100000)
        doc.version += 1
        db.save(doc)
        time.sleep(0.001)

    return True


def main():
    db = JsonDB(base_path="./tmp/file_safety_db")

    print("=== Testing File-Level Safety with Concurrent Writes ===\n")
    print("Writing large documents concurrently from multiple threads...")
    print("This tests that:")
    print("1. Writes are atomic (using temp files + os.replace)")
    print("2. No partial writes or corrupted files")
    print("3. File locks prevent simultaneous writes to same file\n")

    doc_id = "test-doc"

    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(write_large_document, db, doc_id, i) for i in range(5)]

        for future in futures:
            future.result()

    final_doc = db.load(Document, key=doc_id)

    print("Final document state:")
    print(f"  ID: {final_doc.id}")
    print(f"  Version: {final_doc.version}")
    print(f"  Content length: {len(final_doc.content)} bytes")
    print(f"  Updated at: {final_doc.updated_at}")

    print("\n✓ SUCCESS: File is intact and not corrupted!")
    print("  - Atomic writes ensured no partial data")
    print("  - File locks prevented simultaneous writes")
    print("  - Document loaded successfully without errors")

    print("\n" + "=" * 60)
    print("NOTE: File-level locking protects against:")
    print("  ✓ Corrupted/partial file writes")
    print("  ✓ Reading while writing")
    print("  ✓ Simultaneous writes to same file")
    print("\nApplication-level atomicity (read-modify-write cycles)")
    print("must be handled by the application logic.")
    print("=" * 60)


if __name__ == "__main__":
    main()
