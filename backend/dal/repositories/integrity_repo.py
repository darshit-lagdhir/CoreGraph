import hashlib
import uuid
from typing import List, Optional, Tuple
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from dal.models.integrity import MerkleNode


def calculate_canonical_hash(data: dict) -> bytes:
    """Produces a deterministic SHA-256 fingerprint for node attributes."""
    # Strict canonicalization: Sorted keys, no whitespace
    import json

    canonical_str = json.dumps(data, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical_str.encode("utf-8")).digest()


async def generate_merkle_proof(session: AsyncSession, package_id: uuid.UUID) -> List[bytes]:
    """Retrieves the hierarchical hash path (O(log N)) for forensic verification."""
    # Bottom-up traversal from leaf to root
    proof = []

    # 1. Identify leaf node
    res = await session.execute(select(MerkleNode).where(MerkleNode.package_id == package_id))
    current = res.scalars().first()

    while current and current.parent_id:
        # 2. Fetch sibling hash
        # Assuming our tree structure or indices can identify siblings
        # This is a simplification for Task 016
        res_sibling = await session.execute(
            select(MerkleNode.node_hash)
            .where(MerkleNode.parent_id == current.parent_id)
            .where(MerkleNode.id != current.id)
        )
        sibling_hash = res_sibling.scalar()
        if sibling_hash:
            proof.append(sibling_hash)

        # 3. Move up
        res_parent = await session.execute(
            select(MerkleNode).where(MerkleNode.id == current.parent_id)
        )
        current = res_parent.scalars().first()

    return proof


def verify_proof(node_hash: bytes, proof: List[bytes], root_hash: bytes) -> bool:
    """Mathematically asserts node inclusion within the signed graph state."""
    current = node_hash
    for sibling in proof:
        # Standard Merkle hashing: sort siblings to maintain deterministic path
        # Simplification: Assume proof order is correct for breadcrumb reconstruction
        combined = b"".join(sorted([current, sibling]))
        current = hashlib.sha256(combined).digest()

    return current == root_hash
