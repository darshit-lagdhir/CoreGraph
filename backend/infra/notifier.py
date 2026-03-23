import os
import json
import uuid
import datetime
from typing import Dict, Any, Optional
import redis.asyncio as redis
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from dal.models.alerting import AlertEvent, AlertSeverity


class AlertSentinel:
    """
    CoreGraph Proactive Notification Kernel.
    Dispatches high-priority security alarms to the 144Hz HUD with 50ms latency.
    """

    def __init__(self, redis_url: str):
        self.redis_url = redis_url
        self._client: Optional[redis.Redis] = None
        self.channel = "coregraph:alerts:realtime"

    @property
    def client(self) -> redis.Redis:
        if self._client is None:
            self._client = redis.from_url(self.redis_url, decode_responses=False)
        return self._client

    async def aclose(self):
        if self._client:
            await self._client.aclose()
            self._client = None

    async def scream(self, alert_payload: Dict[str, Any]):
        """
        Broadcasts a critical breach signal into the low-latency notification pipe.
        """
        message = json.dumps(alert_payload)
        await self.client.publish(self.channel, message)
        print(f"[SENTINEL] Dispatched security alarm: {alert_payload.get('package_id')}")

    async def trigger_and_persist(
        self,
        session: AsyncSession,
        package_id: uuid.UUID,
        severity: AlertSeverity,
        risk: float,
        criticality: float,
        payload: Dict[str, Any],
    ) -> Optional[AlertEvent]:
        """
        Executes threshold suppression and transactional persistence.
        Ensures cognitive bandwidth is preserved via suppression of redundant alarms.
        """
        # 1. Hysteresis Check / Suppression
        stmt = select(func.count(AlertEvent.id)).where(
            AlertEvent.package_id == package_id,
            AlertEvent.severity == severity,
            AlertEvent.is_acknowledged == False,
        )
        res = await session.execute(stmt)
        if res.scalar() > 0:
            return None

        # 2. Persist Emergency State
        event = AlertEvent(
            package_id=package_id,
            severity=severity,
            risk_snapshot=risk,
            criticality_snapshot=criticality,
            trigger_payload=payload,
        )
        session.add(event)

        # 3. Synchronous Scream for Critical Breaches
        if severity in [AlertSeverity.CRITICAL, AlertSeverity.EMERGENCY]:
            await self.scream(
                {
                    "type": "SECURITY_ALERT",
                    "id": str(event.id),
                    "package_id": str(package_id),
                    "severity": severity,
                    "risk": risk,
                    "criticality": criticality,
                    "context": payload,
                }
            )

        return event


REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
sentinel = AlertSentinel(REDIS_URL)
