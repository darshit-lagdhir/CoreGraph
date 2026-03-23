import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from dal.models.alerting import AlertEvent, AlertSeverity

class AlertRepository:
    """
    CoreGraph Sentinel Module.
    Logs and manages proactive security event triggers. (Task 022).
    """
    def __init__(self, session: AsyncSession):
        self.session = session

    async def log_alert(self, package_id: uuid.UUID, severity: AlertSeverity, risk_snapshot: float, criticality_snapshot: float, trigger_payload: Dict[str, Any]):
        """Persists a high-priority notification to the alerting vault."""
        alert = AlertEvent(
            package_id=package_id,
            severity=severity,
            risk_snapshot=risk_snapshot,
            criticality_snapshot=criticality_snapshot,
            trigger_payload=trigger_payload
        )
        self.session.add(alert)
        await self.session.flush()
        return alert

    async def get_active_alerts(self, min_severity: AlertSeverity = AlertSeverity.INFO) -> List[AlertEvent]:
        """Retrieves unresolved alerts filtered by severity."""
        stmt = select(AlertEvent).where(AlertEvent.is_acknowledged == False).order_by(AlertEvent.created_at.desc())
        res = await self.session.execute(stmt)
        return res.scalars().all()

    async def acknowledge_alert(self, alert_id: uuid.UUID, user_id: uuid.UUID):
        """Marks an alert as acknowledged by an analyst."""
        alert = await self.session.get(AlertEvent, alert_id)
        if alert:
            alert.is_acknowledged = True
            alert.acknowledged_by = user_id
            await self.session.flush()
