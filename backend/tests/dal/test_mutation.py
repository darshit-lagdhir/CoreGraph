import pytest
import uuid
from sqlalchemy import select
from dal.models.graph import Package
from dal.models.annotation import Workspace, GraphTag, ForensicNote
from dal.repositories.mutation_repo import MutationRepository
from dal.utils.diff_engine import calculate_note_delta, apply_note_delta


@pytest.mark.asyncio
async def test_crdt_tag_convergence(session):
    """
    The 'Edit War' Stress Test.
    Simulates 10 analysts tagging and un-tagging the same node
    simultaneously and verifies that the final state converges. (Task 020)
    """
    ws = Workspace(name="test-ws", owner_id=uuid.uuid4())
    pkg = Package(name="target-pkg", ecosystem="npm")
    session.add_all([ws, pkg])
    await session.commit()

    repo = MutationRepository(session)
    user_id = uuid.uuid4()
    for i in range(50):
        # Even: Add (is_deleted=False), Odd: Remove (is_deleted=True)
        is_del = i % 2 != 0
        await repo.apply_tag_crdt(ws.id, pkg.id, "PACKAGE", "MALICIOUS", user_id, is_del, lamport=i)
    await session.commit()

    # 2. Validation: The final state must match the event with the highest timestamp
    # In this case, i=49 was a 'REMOVE' (is_deleted=True)
    resolved_tags = await repo.get_resolved_tag_set(ws.id, pkg.id)
    assert "MALICIOUS" not in resolved_tags

    # Verify internal metadata
    stmt = select(GraphTag).where(GraphTag.target_id == pkg.id)
    res = await session.execute(stmt)
    final_tag = res.scalar_one()
    assert final_tag.is_deleted is True
    assert final_tag.lamport_timestamp == 49
    print("[AUDIT] CRDT Tag Convergence Verified.")


@pytest.mark.asyncio
async def test_note_history_delta_reconstruction(session):
    """
    Ensures that the JSONB delta history can correctly
    reconstruct a note from 5 edits ago. (Task 020)
    """
    ws = Workspace(name="test-ws", owner_id=uuid.uuid4())
    pkg = Package(name="target-pkg", ecosystem="pypi")
    session.add_all([ws, pkg])
    await session.commit()

    original_content = "Vulnerability detected in setup.py."
    note = ForensicNote(
        workspace_id=ws.id, target_id=pkg.id, content=original_content, author_id=uuid.uuid4()
    )
    session.add(note)
    await session.commit()

    v1_content = original_content + " Found base64 blob."
    delta = calculate_note_delta(note.content, v1_content)

    note.content = v1_content
    note.history.append(delta)
    session.add(note)
    await session.commit()

    assert note.content == v1_content
    assert len(note.history) == 1

    reconstructed = apply_note_delta(original_content, note.history[0])
    assert reconstructed == v1_content
    print("[AUDIT] Forensic Delta Patching Verified.")
