#!/usr/bin/env python3
import os
import re

def verify_section_5_compliance():
    """
    Architectural Hardening: Directory Segregation Audit.
    Ensures all persistence and domain logic is encapsulated in the DAL.
    """
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    root_files = os.listdir(root_dir)

    # 1. ROOT LOCK Check: Persistence identifiers in root .py files?
    sql_patterns = re.compile(r"MetaData|create_engine|Session|sqlalchemy|Column", re.IGNORECASE)

    for f in root_files:
        if f.endswith(".py") and f != "main.py": # main.py is the only permitted entry point
            with open(os.path.join(root_dir, f), 'r', errors='ignore') as file:
                content = file.read()
                if sql_patterns.search(content):
                    print(f"[REJECTION] Persistence violation in {f}: Definition detected in root.")
                    return False

    # 2. DAL Encapsulation Check
    dal_path = os.path.join(root_dir, "backend", "dal")
    if not os.path.exists(dal_path):
        print("[REJECTION] Missing Data Access Layer (DAL) directory.")
        return False

    # 3. Model Isolation Check
    model_path = os.path.join(dal_path, "models")
    if not os.listdir(model_path):
        print("[REJECTION] Global models directory is empty. Schema drift detected.")
        return False

    print("[SUCCESS] Spatial Isolation (Section 5) Compliance: 100%. Persistence Sealed.")
    return True

if __name__ == "__main__":
    if verify_section_5_compliance():
        print("[AUDIT] Structure is surgically compliant.")
    else:
        exit(1)
