import uuid
import datetime
from typing import List, Optional
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from dal.models.backup import BackupLedger, BackupStatus, BackupType

class BackupRepository:
    """
    CoreGraph Resilience Module.
    Manages the Point-in-Time Recovery (PITR) ledger and physical backup events. (Task 024).
    """
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_ledger_entry(self, backup_type: BackupType, start_lsn: str, total_size: int = 0) -> BackupLedger:
        """Initializes a new physical backup event in the resilience registry."""
        entry = BackupLedger(
            backup_type=backup_type,
            status=BackupStatus.IN_PROGRESS,
            start_lsn=start_lsn,
            total_size_bytes=total_size
        )
        self.session.add(entry)
        await self.session.flush()
        return entry

    async def complete_backup(self, ledger_id: uuid.UUID, end_lsn: str, compressed_size: int, manifest_hash: bytes):
        """Finalizes the physical backup event with cryptographic hashes."""
        entry = await self.session.get(BackupLedger, ledger_id)
        if entry:
            entry.status = BackupStatus.SUCCESS
            entry.end_lsn = end_lsn
            entry.compressed_size_bytes = compressed_size
            entry.manifest_hash = manifest_hash
            await self.session.flush()

    async def get_latest_lsn(self) -> str:
        """Retrieves the most recent Point-in-Time recovery marker."""
        res = await self.session.execute(select(func.max(BackupLedger.start_lsn)))
        return res.scalar() or "0/0"
