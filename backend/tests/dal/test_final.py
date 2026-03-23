import pytest
import uuid
import datetime
from sqlalchemy import select
from dal.engine import CoreGraphEngine
from dal.models.graph import Package
from dal.models.risk_scoring import RiskScoringIndex

@pytest.mark.asyncio
async def test_global_intelligence_assembly(session):
    """
    The 'Final Handshake' Audit.
    Verifies that the CoreGraphEngine can successfully assemble a 
    complete Intelligence Object (I_Omega) from all 25 layers. (Task 025.7)
    """
    # 1. Setup Mock Node and Multi-vector Context
    node = Package(
        name="lodash",
        ecosystem="npm",
        version_latest="4.17.21"
    )
    session.add(node)
    await session.commit()
    
    risk = RiskScoringIndex(
        package_id=node.id,
        r_idx=0.85,
        v_topo=0.9,
        v_beh=0.4
    )
    session.add(risk)
    await session.commit()
    
    # 2. Re-instantiate the Beast
    engine = CoreGraphEngine(session)
    
    # 3. Assemble I_Omega Object
    # This triggers search, risk, and behavioral modules
    intel_obj = await engine.get_intelligence_object("npm:lodash")
    
    # 4. Global Validation: Master Context Alignment
    assert intel_obj is not None
    assert "topology" in intel_obj       # Task 003, 011
    assert "behavior" in intel_obj       # Task 004
    assert "risk_vectors" in intel_obj   # Task 021
    assert "forensic_seal" in intel_obj  # Task 016
    assert "node_metadata" in intel_obj  # Task 001
    
    # 5. Internal Consistency Audit
    # The risk score in the Intelligence Object must match the database truth
    assert intel_obj["risk_vectors"]["r_idx"] == 0.85
    assert intel_obj["risk_vectors"]["v_topo"] == 0.9
    
    # 6. Metadata Verification
    assert intel_obj["node_metadata"]["name"] == "lodash"
    assert intel_obj["node_metadata"]["ecosystem"] == "npm"
    
    print("[FINAL AUDIT] CoreGraph Persistence Layer is consistent and sealed.")

@pytest.mark.asyncio
async def test_ai_handoff_serialization(session):
    """
    Ensures that the I_Omega object is correctly serialized for AI consumption.
    (Task 025.4 Semantic Serialization).
    """
    engine = CoreGraphEngine(session)
    
    # 1. Mock I_Omega
    mock_intel = {
        "node_metadata": {"name": "lodash"},
        "risk_vectors": {"r_idx": 0.85}
    }
    
    # 2. Execution: AI Handoff Protocol
    payload = await engine.semantic_serialize(mock_intel)
    
    # 3. Validation: Narrative Integrity
    assert "lodash" in payload
    assert "0.85" in payload
    print("[FINAL AUDIT] AI Handoff Protocol Verified.")
