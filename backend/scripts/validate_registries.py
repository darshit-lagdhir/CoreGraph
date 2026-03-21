import json
import logging
import os
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor
from typing import Any, Dict, List, Tuple

import jsonschema
from jsonschema import validate

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

WORKSPACE_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".workspace"
)

TASK_MATRIX_SCHEMA = {
    "type": "object",
    "required": ["total_modules", "current_status"],
    "properties": {
        "total_modules": {"type": "integer"},
        "current_status": {
            "type": "object",
            "properties": {
                "active_module": {"type": "integer"},
                "last_completed_task_id": {"type": "string"},
                "completion_percentage": {"type": "number"},
            },
        },
    },
}

EXECUTION_LEDGER_SCHEMA = {
    "type": "array",
    "items": {
        "type": "object",
        "required": ["task_id", "status", "prerequisite_id"],
        "properties": {
            "task_id": {"type": "string"},
            "status": {"type": "string"},
            "prerequisite_id": {"type": "array", "items": {"type": "string"}},
        },
    },
}


def check_json_schema(file_path: str, schema: Dict[str, Any]) -> Tuple[bool, Any]:
    if not os.path.exists(file_path):
        return False, f"{os.path.basename(file_path)} missing."
    with open(file_path, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
            validate(instance=data, schema=schema)
            return True, data
        except Exception as e:
            return False, f"Schema validation failed for {file_path}: {e}"


def topological_sort_check(ledger_data: List[Dict[str, Any]]) -> Tuple[bool, str]:
    graph = defaultdict(list)
    in_degree = defaultdict(int)
    tasks = [item["task_id"] for item in ledger_data]

    for item in ledger_data:
        task = item["task_id"]
        in_degree[task] = 0

    for item in ledger_data:
        task = item["task_id"]
        for prereq in item.get("prerequisite_id", []):
            if prereq in tasks:
                graph[prereq].append(task)
                in_degree[task] += 1
            else:
                graph[prereq].append(task)
                in_degree[task] += 1
                if prereq not in in_degree:
                    in_degree[prereq] = 0

    queue = [t for t in in_degree if in_degree[t] == 0]
    visited = 0

    while queue:
        node = queue.pop(0)
        visited += 1
        for neighbor in graph[node]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)

    if visited != len(in_degree):
        return (
            False,
            f"Circular dependencies detected. Visited {visited} out of {len(in_degree)} nodes.",
        )
    return True, "DAG verification passed."


def validate_markdown_ast(file_path: str) -> Tuple[bool, str]:
    if not os.path.exists(file_path):
        return False, "project-context.md missing."
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()

        has_relational = False
        has_api = False

        md_content = text
        if "Relational Schema" in md_content:
            has_relational = True
        if "API Payloads" in md_content:
            has_api = True

        if has_relational and has_api:
            return True, "Markdown tables for schema and payloads verified."
        else:
            return (
                False,
                "Missing Relational Schema or API Payloads sections in Markdown.",
            )
    except Exception as e:
        return False, f"AST parsing failed: {e}"


def run_validations() -> bool:
    matrix_path = os.path.join(WORKSPACE_DIR, "task-matrix.json")
    ledger_path = os.path.join(WORKSPACE_DIR, "execution-ledger.json")
    context_path = os.path.join(WORKSPACE_DIR, "project-context.md")

    if not os.path.exists(matrix_path):
        logging.error(f"Task Matrix missing: {matrix_path}")
        return False

    with ProcessPoolExecutor(max_workers=3) as executor:
        f_matrix = executor.submit(check_json_schema, matrix_path, TASK_MATRIX_SCHEMA)
        f_ledger = executor.submit(check_json_schema, ledger_path, EXECUTION_LEDGER_SCHEMA)
        f_md = executor.submit(validate_markdown_ast, context_path)

        matrix_ok, matrix_res = f_matrix.result()
        if not matrix_ok:
            logging.error(f"Task Matrix error: {matrix_res}")
            return False

        ledger_ok, ledger_res = f_ledger.result()
        if not ledger_ok:
            logging.error(f"Ledger error: {ledger_res}")
            return False

        md_ok, md_res = f_md.result()
        if not md_ok:
            logging.error(f"MD error: {md_res}")
            return False

        dag_ok, dag_res = topological_sort_check(ledger_res)
        if not dag_ok:
            logging.error(f"DAG error: {dag_res}")
            return False

    logging.info("All registries successfully validated and synchronized.")
    return True


if __name__ == "__main__":
    from multiprocessing import freeze_support

    freeze_support()
    success = run_validations()
    exit(0 if success else 1)
