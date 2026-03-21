import pytest
import asyncio
import time
from sqlalchemy import text
from infra.database import db_manager


@pytest.mark.asyncio
async def test_pool_concurrency_stress():
    """
    The 'Beast' Stress Test for the i9-13980hx Highway.
    Simulates concurrent users and verifies that the pool handles overflow.
    """

    async def concurrent_task(task_id: int):
        # MUST USE async for with the generator as originally architected
        async for session in db_manager.get_session():
            result = await session.execute(text("SELECT pg_sleep(0.01)"))
            assert result is not None
            return True

    # Use 25 tasks for LITE stability
    tasks = [concurrent_task(i) for i in range(25)]

    start = time.perf_counter()
    results = await asyncio.gather(*tasks, return_exceptions=True)
    end = time.perf_counter()

    errors = [r for r in results if isinstance(r, Exception)]
    assert (
        len(errors) == 0
    ), f"Concurrency test failed with {len(errors)} errors: {errors[0] if errors else ''}"

    print(f"\nPool Stress Test Complete: 25 queries in {end-start:.2f}s")
