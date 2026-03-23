import uuid
import hashlib
import json
from typing import List, Dict, Any, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from dal.models.integrity import MerkleNode


class IntegrityRepository:
    """
    CoreGraph Forensic Module.
    Enforces cryptographic trust via Merkle-tree inclusion proofs.
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    async def generate_merkle_proof(self, package_id: uuid.UUID) -> List[str]:
        """
        Retrieves the hierarchical hash path (O(log N)) for forensic verification.
        Converts bytes to hex strings for token-efficient AI handoff. (Task 025.4)
        """
        proof = []
        res = await self.session.execute(
            select(MerkleNode).where(MerkleNode.package_id == package_id)
        )
        current = res.scalars().first()

        while current and current.parent_id:
            res_sibling = await self.session.execute(
                select(MerkleNode.node_hash)
                .where(MerkleNode.parent_id == current.parent_id)
                .where(MerkleNode.id != current.id)
            )
            sibling_hash = res_sibling.scalar()
            if sibling_hash:
                proof.append(sibling_hash.hex())

            res_parent = await self.session.execute(
                select(MerkleNode).where(MerkleNode.id == current.parent_id)
            )
            current = res_parent.scalars().first()

        return proof

    def calculate_canonical_hash(self, data: Dict[str, Any]) -> str:
        """Produces a deterministic SHA-256 fingerprint for node attributes."""
        canonical_str = json.dumps(data, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(canonical_str.encode("utf-8")).hexdigest()

    def verify_proof(self, node_hash: str, proof: List[str], root_hash: str) -> bool:
        """Mathematically asserts node inclusion within the signed graph state."""
        current = node_hash
        for sibling in proof:
            combined = "".join(sorted([current, sibling]))
            current = hashlib.sha256(combined.encode()).hexdigest()
        return current == root_hash
