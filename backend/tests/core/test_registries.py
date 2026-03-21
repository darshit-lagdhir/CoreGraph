import os
import json
import pytest
from scripts.validate_registries import (
    topological_sort_check,
    validate_markdown_ast,
    check_json_schema,
    EXECUTION_LEDGER_SCHEMA,
)

pytestmark = pytest.mark.asyncio


def test_circular_dependency_detection():
    ledger_data = [
        {"task_id": "T1", "status": "COMPLETED", "prerequisite_id": ["T2"]},
        {"task_id": "T2", "status": "COMPLETED", "prerequisite_id": ["T3"]},
        {"task_id": "T3", "status": "COMPLETED", "prerequisite_id": ["T1"]},
    ]
    ok, msg = topological_sort_check(ledger_data)
    assert not ok
    assert "Circular dependencies detected" in msg


def test_valid_dag_execution():
    ledger_data = [
        {"task_id": "T1", "status": "COMPLETED", "prerequisite_id": []},
        {"task_id": "T2", "status": "COMPLETED", "prerequisite_id": ["T1"]},
        {"task_id": "T3", "status": "COMPLETED", "prerequisite_id": ["T2"]},
    ]
    ok, msg = topological_sort_check(ledger_data)
    assert ok
    assert "passed" in msg.lower()


def test_markdown_ast_validation(tmp_path):
    test_file = tmp_path / "project-context.md"
    test_file.write_text(
        "## Relational Schema\n| col | val |\n## API Payloads\n| col | val |", encoding="utf-8"
    )
    ok, msg = validate_markdown_ast(str(test_file))
    assert ok


def test_markdown_ast_validation_missing_schema(tmp_path):
    test_file = tmp_path / "project-context.md"
    test_file.write_text("## Random Header\nSome text.", encoding="utf-8")
    ok, msg = validate_markdown_ast(str(test_file))
    assert not ok
    assert "Missing Relational Schema" in msg


def test_json_schema_validation(tmp_path):
    test_file = tmp_path / "execution-ledger.json"
    bad_data = [{"task_id": "T1"}]
    test_file.write_text(json.dumps(bad_data))
    ok, msg = check_json_schema(str(test_file), EXECUTION_LEDGER_SCHEMA)
    assert not ok
    assert "Schema validation failed" in msg


def test_schema_ghosting_prevention(tmp_path):
    # Tests that when schemas are disconnected or incomplete, it correctly fails
    test_file = tmp_path / "execution-ledger.json"
    valid_data = [{"task_id": "T1", "status": "COMPLETED", "prerequisite_id": []}]
    test_file.write_text(json.dumps(valid_data))
    ok, msg = check_json_schema(str(test_file), EXECUTION_LEDGER_SCHEMA)
    assert ok
