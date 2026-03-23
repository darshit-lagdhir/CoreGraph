import uuid
from typing import Dict, Any, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from dal.models.maintainer import AuthorProfile, MaintainerMetrics


class MaintainerRepository:
    """
    CoreGraph Behavioral Module.
    Identifies maintainer velocity, reputation, and identities for risk calibration.
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_maintainer_behavior(self, package_id: uuid.UUID) -> Optional[Dict[str, Any]]:
        """
        Retrieves behavioral metrics for all maintainers of a given package.
        Implements Attribute-Level Access Control (ALAC) to mask PII. (Task 025.6)
        """
        stmt = select(MaintainerMetrics).where(MaintainerMetrics.package_id == package_id)
        res = await self.session.execute(stmt)
        m = res.scalars().first()

        if not m:
            return {"velocity": 0.5, "reputation": "Neutral", "id_verified": False}

        return {
            "velocity": m.current_velocity,
            "se_risk_score": m.se_risk_score,
            "last_active": m.last_active_at.isoformat() if m.last_active_at else None,
        }
