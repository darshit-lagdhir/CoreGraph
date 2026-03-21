import asyncio  # noqa: E402
import sys  # noqa: E402
import os  # noqa: E402

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), "backend"))

from database import engine, AsyncSessionLocal  # noqa: E402
from sqlalchemy import text  # noqa: E402


async def execute_query(session_id: int):
    try:
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))
            await asyncio.sleep(0.5)
    except Exception as e:
        print(f"Exception sequence failed on {session_id}: {e}")
        return False
    return True


async def stress_test():
    print("Initiating 50 concurrent asynchronous connections mapped to primary pool arrays...")
    tasks = [execute_query(i) for i in range(50)]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    success_count = sum(1 for r in results if r is True)
    if success_count == 50:
        print("Success: Overflow handling actively neutralizes connection latency constraints.")
        sys.exit(0)
    else:
        print(f"Failure: Detected {success_count}/50 bounds connected securely.")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(stress_test())
