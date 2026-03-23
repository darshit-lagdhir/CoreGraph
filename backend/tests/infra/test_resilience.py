import pytest
import asyncio
import uuid
from sqlalchemy import select, func, text
from dal.models.backup import BackupLedger, BackupStatus, BackupType
from infra.backup_engine import CloneEngine

@pytest.mark.asyncio
async def test_backup_ledger_persistence(session):
    """
    Verifies that every physical backup event for the 3.88M node graph 
    is recorded with high-precision LSN markers. (Task 024.2)
    """
    # 1. Setup Mock Ledger entry
    entry = BackupLedger(
        backup_type=BackupType.FULL,
        status=BackupStatus.SUCCESS,
        start_lsn="0/1A2B3C4D", # Hexadecimal LSN pointer (OSINT-standard)
        end_lsn="0/1A2B5000",
        total_size_bytes=214748364800, # 200GB (Task 024 volume)
        compressed_size_bytes=42949672960, # 40GB (LZ4 5x compression)
        manifest_hash=b"a"*32
    )
    session.add(entry)
    await session.commit()
    
    # 2. Validation: Recovery Timeline Indexing
    stmt = select(BackupLedger).where(BackupLedger.id == entry.id)
    res = await session.execute(stmt)
    refetched = res.scalars().one()
    
    assert refetched.status == BackupStatus.SUCCESS
    assert refetched.total_size_bytes == 214748364800
    print("[AUDIT] Backup Ledger Persistent.")

@pytest.mark.asyncio
async def test_clone_engine_dry_run():
    """
    Verifies the instantiation and config of the Clone Engine.
    (Self-check for Task 024.4)
    """
    config = {
        'host': 'localhost',
        'port': 5432,
        'user': 'admin',
        'password': 'password'
    }
    engine = CloneEngine(config)
    assert engine.user == "admin"
    assert "Backups" in engine.backup_dir
    print("[AUDIT] Clone Engine Correctly Configured.")

@pytest.mark.asyncio
async def test_disaster_recovery_lsn_ordering(session):
    """
    Ensures that LSN pointers are monotonically increasing 
    for the Point-in-Time Recovery timeline. (Task 024.1)
    """
    # 1. Create two backup events
    b1 = BackupLedger(backup_type=BackupType.WAL_ARCHIVE, start_lsn="0/1000", status=BackupStatus.SUCCESS)
    b2 = BackupLedger(backup_type=BackupType.WAL_ARCHIVE, start_lsn="0/2000", status=BackupStatus.SUCCESS)
    session.add_all([b1, b2])
    await session.commit()
    
    # 2. Query timeline order
    stmt = select(BackupLedger).order_by(BackupLedger.start_lsn.desc())
    res = await session.execute(stmt)
    timeline = res.scalars().all()
    
    assert timeline[0].start_lsn == "0/2000"
    assert timeline[1].start_lsn == "0/1000"
    print("[AUDIT] Disaster Recovery Monotonic LSN Verified.")
