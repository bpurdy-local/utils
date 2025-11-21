import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

from pydantic import BaseModel

from utils import Index, JsonDB


class Counter(BaseModel):
    id: str = Index()
    count: int
    updated_at: datetime


def increment_counter(db: JsonDB, worker_id: int, iterations: int) -> int:
    local_increments = 0
    for i in range(iterations):
        counter = db.load(Counter, key="shared")
        if counter:
            counter.count += 1
            counter.updated_at = datetime.now()
            db.save(counter)
            local_increments += 1
        time.sleep(0.001)
    return local_increments


def main():
    db = JsonDB(base_path="./tmp/concurrent_test_db")

    print("=== Testing Concurrent Access with File Locking ===\n")

    counter = Counter(id="shared", count=0, updated_at=datetime.now())
    db.save(counter)

    print("Initial counter value: 0")
    print("Running 10 workers, each incrementing 50 times...")
    print("Expected final value: 500\n")

    num_workers = 10
    iterations_per_worker = 50

    with ThreadPoolExecutor(max_workers=num_workers) as executor:
        futures = [
            executor.submit(increment_counter, db, worker_id, iterations_per_worker)
            for worker_id in range(num_workers)
        ]

        total_increments = 0
        for future in as_completed(futures):
            total_increments += future.result()

    final_counter = db.load(Counter, key="shared")

    print(f"Total increments performed: {total_increments}")
    print(f"Final counter value: {final_counter.count}")
    print(f"Difference: {total_increments - final_counter.count}")

    if final_counter.count == total_increments:
        print("\n✓ SUCCESS: No race conditions detected!")
        print("  File locking is working correctly.")
    else:
        print("\n✗ FAILURE: Race condition detected!")
        print(f"  Lost {total_increments - final_counter.count} updates")

    print("\nFinal state:")
    print(f"  Count: {final_counter.count}")
    print(f"  Last updated: {final_counter.updated_at}")


if __name__ == "__main__":
    main()
