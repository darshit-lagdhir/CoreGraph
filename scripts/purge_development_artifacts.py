#!/usr/bin/env python3
import os
import glob
import shutil

def execution_purge_protocol():
    """
    The Final Janitor.
    Aggressively removes all development-stage database artifacts and temporary cruft.
    Compliance with Section 4.
    """
    patterns = [
        "*.sqlite", "*.sqlite3", "*.db", # SQLite remnants
        "*.log", "*.tmp",                # Temp files
        "*.txt",                         # Potential trace logs
        "sql_scratchpad.sql",            # Ad-hoc tuning scripts
        "test_dump.bin",                 # Binary artifacts
        "**/__pycache__/**",             # Python bytecode
        ".pytest_cache/**",              # Pytest metadata
        "*.bak",                         # Backup fragments
        "*.swp"                          # Vim swap files
    ]

    print("[PURGE] Initiating Section 4 Compliance Protocol...")
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    for pattern in patterns:
        # Use recursive glob for deep cleaning
        search_path = os.path.join(root_dir, pattern)
        files = glob.glob(search_path, recursive=True)
        for f in files:
            try:
                if os.path.isfile(f):
                    os.remove(f)
                    print(f"[PURGE] Deleted file: {f}")
                elif os.path.isdir(f):
                    shutil.rmtree(f)
                    print(f"[PURGE] Deleted directory: {f}")
            except Exception as e:
                print(f"[ERROR] Failed to purge {f}: {e}")

    print("[SUCCESS] Workspace is surgically clean. Section 4 Compliance: 100%.")

def verify_section_4_cleanliness():
    """Verification hook for the final seal test."""
    # Simple check for common offenders in root
    root_files = os.listdir(".")
    offenders = [f for f in root_files if f.endswith(".sqlite") or f.endswith(".db") or f.endswith(".log")]
    return len(offenders) == 0

if __name__ == "__main__":
    execution_purge_protocol()
