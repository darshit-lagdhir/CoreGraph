import uuid
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from dal.models.export import ExportJob, ExportArtifact, ExportStatus, ExportFormat

class ExportRepository:
    """
    CoreGraph Forensic Output Module.
    Manages the lifecycle of SBOM Generation and OSINT Report Bundling. (Task 023).
    """
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_job(self, workspace_id: uuid.UUID, requestor_id: uuid.UUID, format: ExportFormat, scope: str = "*") -> ExportJob:
        """Initializes a forensic export job."""
        job = ExportJob(
            workspace_id=workspace_id,
            requestor_id=requestor_id,
            format=format,
            status=ExportStatus.PROCESSING,
            scope_query=scope
        )
        self.session.add(job)
        await self.session.flush()
        return job

    async def record_artifact(self, job_id: uuid.UUID, filename: str, checksum: str, size: int) -> ExportArtifact:
        """Registers a persistent forensic artifact (CGBUNDLE)."""
        artifact = ExportArtifact(
            export_job_id=job_id,
            filename=filename,
            sha256_checksum=checksum,
            size_bytes=size
        )
        self.session.add(artifact)
        await self.session.flush()
        return artifact

    async def complete_job(self, job_id: uuid.UUID, status: ExportStatus = ExportStatus.COMPLETED):
        """Finalizes the job lifecycle."""
        import datetime
        job = await self.session.get(ExportJob, job_id)
        if job:
            job.status = status
            if status == ExportStatus.COMPLETED:
                job.completed_at = datetime.datetime.utcnow()
            await self.session.flush()
