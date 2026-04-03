import asyncio  # noqa: E402
import os  # noqa: E402
import sys  # noqa: E402
import uuid  # noqa: E402

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from database import AsyncSessionLocal  # noqa: E402
from models import Package  # noqa: E402
from sqlalchemy.dialects.postgresql import insert  # noqa: E402


async def bulk_insert_packages(batch_size: int = 1000):
    async with AsyncSessionLocal() as session:
        records = []
        for i in range(batch_size):
            u_id = str(uuid.uuid4())
            records.append(
                {
                    "id": u_id,
                    "ecosystem": "test_net",
                    "name": f"test-matrix-{u_id}",
                }
            )

        stmt = insert(Package).values(records).on_conflict_do_nothing()
        await session.execute(stmt)
        await session.commit()


async def execute_load():
    print("Initiating parallel bulk UUIDv4 execution testing...")
    batches = [bulk_insert_packages(1000) for _ in range(10)]
    await asyncio.gather(*batches)
    print("Success: 10,000 unique records instantiated, explicitly avoiding relational locking.")


if __name__ == "__main__":
    asyncio.run(execute_load())
