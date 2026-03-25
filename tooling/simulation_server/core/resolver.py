import base64
import struct
from typing import Optional, Tuple

class CursorResolver:
    """
    S.U.S.E. Cursor-Based Pagination Kernel (Task 021).
    Opaque Cursor Determinism using Seed-Anchored XOR Salting.
    """
    def __init__(self, master_seed: int = 0xDEADC0DE):
        self.master_seed = master_seed

    def encode_cursor(self, index: int) -> str:
        """
        Encoding Integer Index into Opaque Base64 String.
        XORed with Master Seed for Deterministic Salting.
        """
        # 64-bit salting to prevent easy guessing
        salted = index ^ self.master_seed
        # Packing into binary and base64 encoding
        binary = struct.pack("<Q", salted)
        return base64.b64encode(binary).decode('utf-8')

    def decode_cursor(self, cursor: str) -> int:
        """
        Decoding Opaque Base64 String into Integer Index.
        Reverses XOR Salting to find the Global Offset.
        """
        try:
            binary = base64.b64decode(cursor)
            salted = struct.unpack("<Q", binary)[0]
            index = salted ^ self.master_seed
            return index
        except Exception:
            # Return 0 if cursor is malformed or invalid
            return 0

    def calculate_slice(self, first: int, after: Optional[str] = None, total_nodes: int = 10000) -> Tuple[int, int, bool]:
        """
        Constant-Time Slice Calculation (O(1)).
        Returns: (start_index, end_index, has_next_page)
        """
        start_index = 0
        if after:
            start_index = self.decode_cursor(after) + 1
        
        # Enforce GitHub-style 100-node limit
        limit = min(first, 100)
        end_index = min(start_index + limit, total_nodes)
        
        has_next_page = end_index < total_nodes
        
        return start_index, end_index, has_next_page

if __name__ == "__main__":
    resolver = CursorResolver()
    print("──────── CURSOR DETERMINISM AUDIT ─────────")
    # Test encoding/decoding
    c1 = resolver.encode_cursor(99)
    print(f"[RESOLVER] Index 99 -> Cursor: {c1}")
    idx = resolver.decode_cursor(c1)
    print(f"[RESOLVER] Decoded: {idx}")
    
    # Test slicing
    start, end, exists = resolver.calculate_slice(first=100, after=c1, total_nodes=1000)
    print(f"[SLICER] After '{c1}' (Index 99), Fetch 100 -> Range: {start}-{end} | Next: {exists}")
