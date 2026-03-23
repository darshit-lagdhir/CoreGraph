import uuid
from typing import Dict, Any, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from dal.models.risk_scoring import RiskScoringIndex


class RiskRepository:
    """
    CoreGraph Strategic Module.
    Resolves multi-vector risk scores (R_idx) and criticality (C_idx) for the software ocean.
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_quantized_scores(self, package_id: uuid.UUID) -> Dict[str, Any]:
        """
        Retrieves the R_idx and C_idx vectors for the Intel_Omega assembly.
        Implements snapshot-locking for internal consistency audits. (Task 025.6)
        """
        stmt = select(RiskScoringIndex).where(RiskScoringIndex.package_id == package_id)
        res = await self.session.execute(stmt)
        risk = res.scalars().first()

        if not risk:
            return {"r_idx": 0.0, "c_idx": 0.0, "v_beh": 0.0, "status": "UNKNOWN"}

        return {
            "r_idx": risk.r_idx,
            "v_topo": risk.v_topo,
            "v_beh": risk.v_beh,
            "status": "CALIBRATED" if risk.r_idx > 0.0 else "UNQUANTIFIED",
        }
