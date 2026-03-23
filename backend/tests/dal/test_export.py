import pytest
import os
import uuid
import json
import zstandard as zstd
from sqlalchemy import text
from dal.models.export import ExportJob, ExportStatus, ExportFormat
from dal.utils.sbom_mapper import SBOMMapper
from dal.utils.bundler import ForensicBundler


@pytest.mark.asyncio
async def test_sbom_compliance_integrity():
    """
    Verifies that the generated SBOM artifact contains
    proprietary CoreGraph extension properties correctly formatted.
    """
    mapper = SBOMMapper()

    # 1. Generate a mock export artifact
    mock_node = {
        "name": "test-lib",
        "version": "1.0.0",
        "ecosystem": "npm",
        "sha256_checksum": "a" * 64,
    }
    risk_data = {"r_idx": 0.85, "c_idx": 0.9, "v_beh": 0.5, "merkle_root": "0x5467..."}

    sbom_component = mapper.map_node_to_cyclonedx(mock_node, risk_data)

    # 2. Validation: Properties must exist and match
    props = {p["name"]: p["value"] for p in sbom_component["properties"]}
    assert props["coregraph:risk_score"] == "0.85"
    assert props["coregraph:provenance_root"] == "0x5467..."
    assert sbom_component["name"] == "test-lib"
    print("[AUDIT] SBOM Schema Compliance Verified.")


@pytest.mark.asyncio
async def test_bundle_signature_verification():
    """
    Ensures that the Ed25519 signature of a .cgbundle is
    mathematically verifiable. (Task 023.2)
    """
    bundler = ForensicBundler()

    # 1. Create mock payload and sign it
    payload = b"CoreGraph Forensic OSINT Archive Manifest v1.0"
    signature = bundler.sign_payload(payload)

    # 2. Compress and generate bundle
    compressed = bundler.compressor.compress(payload)

    # 3. Verification using Public Key
    is_valid = await bundler.verify_bundle(
        compressed, signature, bundler.signing_key.verify_key.encode()
    )
    assert is_valid is True

    # 4. Tamper Test
    tampered = payload + b" EXTRA_DATA"
    is_valid_tamper = await bundler.verify_bundle(
        bundler.compressor.compress(tampered), signature, bundler.signing_key.verify_key.encode()
    )
    assert is_valid_tamper is False
    print("[AUDIT] Ed25519 Forensic Signature Verified.")


@pytest.mark.asyncio
async def test_export_job_lifecycle(session):
    """
    Verifies the persistence of export jobs and their status tracking.
    """
    # 1. Create Job (Setup Workspace first)
    from dal.models.annotation import Workspace

    ws = Workspace(name="forensic-unit-01", owner_id=uuid.uuid4())
    session.add(ws)
    await session.commit()

    job = ExportJob(
        workspace_id=ws.id,
        requestor_id=uuid.uuid4(),
        format=ExportFormat.COREGRAPH_FORENSIC,
        status=ExportStatus.PROCESSING,
        scope_query="BOX(0,0,0, 10,10,10)",
    )
    session.add(job)
    await session.commit()

    # 2. Update status and verify completion
    job.status = ExportStatus.COMPLETED
    res = await session.execute(text("SELECT NOW()"))
    job.completed_at = res.scalar()
    await session.commit()

    # Check
    refetched = await session.get(ExportJob, job.id)
    assert refetched.status == ExportStatus.COMPLETED
    print("[AUDIT] Export Job Lifecycle Persistent.")
