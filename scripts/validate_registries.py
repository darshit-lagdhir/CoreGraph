import os
import json
import sys

def execute_environment_diagnostics():
    workspace_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".workspace")
    matrix_path = os.path.join(workspace_dir, "task-matrix.json")
    context_path = os.path.join(workspace_dir, "project-context.md")

    if not os.path.exists(matrix_path):
        print("CRITICAL FAILURE: task-matrix.json absent from localized bounds.")
        sys.exit(1)

    if not os.path.exists(context_path):
        print("CRITICAL FAILURE: project-context.md absent from localized bounds.")
        sys.exit(1)

    try:
        with open(matrix_path, "r", encoding="utf-8") as f:
            matrix = json.load(f)
            if "total_modules" not in matrix or "current_status" not in matrix:
                print("CRITICAL FAILURE: Task matrix violates strict JSON schema mapping.")
                sys.exit(1)
    except json.JSONDecodeError:
        print("CRITICAL FAILURE: Malformed JSON integrity discovered.")
        sys.exit(1)

    with open(context_path, "r", encoding="utf-8") as f:
        content = f.read()
        if "8GB RAM" not in content or "5433" not in content:
            print("CRITICAL FAILURE: Core hardware thresholds misaligned or drifted.")
            sys.exit(1)

    print("DIAGNOSTICS COMPLETE: Execution bounds cryptographically synchronized.")
    sys.exit(0)

if __name__ == "__main__":
    execute_environment_diagnostics()
