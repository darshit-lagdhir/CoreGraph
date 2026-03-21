import sys  # noqa: E402
import os  # noqa: E402

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from worker import celery_app  # noqa: E402


def execute_load_matrix():
    print("Initiating 1,000 parallel ingestion seeds testing Redis broker constraints...")
    tasks = []

    for i in range(1000):
        res = celery_app.send_task(
            "tasks.ingestion.enrich_node_telemetry",
            args=["npm", [i]],
            queue="ingestion",
        )
        tasks.append(res)

    print("Tasks successfully routed entirely bypassing primary web loops.")
    sys.exit(0)


if __name__ == "__main__":
    execute_load_matrix()
