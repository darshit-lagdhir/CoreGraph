import pytest
from pydantic import ValidationError
from datetime import datetime
import uuid

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from schemas import PackageSchema, IngestRequestSchema

def test_package_schema_integrity():
    schema = PackageSchema(
        id=uuid.uuid4(),
        ecosystem="npm",
        name="react",
        latest_version="18.2.0",
        created_at=datetime.utcnow()
    )
    assert schema.ecosystem == "npm"

def test_package_schema_boundary_limit():
    with pytest.raises(ValidationError):
        PackageSchema(
            id=uuid.uuid4(),
            ecosystem="npm" * 50, # Threatens the 50 char string limit
            name="react",
            created_at=datetime.utcnow()
        )
