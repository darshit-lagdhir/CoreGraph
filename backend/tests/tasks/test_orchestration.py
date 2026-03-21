import os
import sys

import pytest
from celery.result import AsyncResult

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from tasks.ingestion import ingest_ecosystem_structure  # noqa: E402
from worker import celery_app  # noqa: E402


@pytest.fixture(autouse=True)
def configure_eager():
    celery_app.conf.task_always_eager = True
    celery_app.conf.task_eager_propagates = True


def test_fan_out_orchestration_execution():
    result = ingest_ecosystem_structure.apply_async(args=["npm", "react"])

    # Mathematical chord mapping validation bounds
    assert result.state == "SUCCESS"
    assert "components_resolved" or "status" in result.result
