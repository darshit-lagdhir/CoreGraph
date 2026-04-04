import os
from typing import Dict, Any

# Module 11 - Task 01: Interface Constants
# Silicon-native calibrations for the Egress Gear-Box

INTERFACE_CONFIG: Dict[str, Any] = {
    "REDLINE": {
        "CHUNK_SIZE": 1024 * 1024,  # 1MB
        "YIELD_INTERVAL": 0,  # Saturate Pipe
        "CONCURRENCY_LIMIT": 64,
    },
    "MIDRANGE": {
        "CHUNK_SIZE": 64 * 1024,  # 64KB
        "YIELD_INTERVAL": 0.001,  # 1ms
        "CONCURRENCY_LIMIT": 16,
    },
    "POTATO": {
        "CHUNK_SIZE": 8 * 1024,  # 8KB
        "YIELD_INTERVAL": 0.005,  # 5ms
        "CONCURRENCY_LIMIT": 2,
    },
}

if __name__ == "__main__":
    print(f"\n[+] INTERFACE CONFIGURATION LOADED: {list(INTERFACE_CONFIG.keys())}")
