import os
import json
import uuid
import logging
import redis.asyncio as redis
from datetime import datetime
from typing import Dict, Any, Optional, Callable, Awaitable

# CoreGraph Event System for the i9-13980hx Workstation
# Utilizes Redis Streams (Decoupled, Persistent, and High-Throughput)


class EventBus:
    """
    The Central Nervous System of CoreGraph.
    Manages the distribution of real-time security signals and ingestion events.
    """

    def __init__(self):
        self.redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        self.client = redis.from_url(self.redis_url, decode_responses=True)
        self.stream_name = "coregraph_events"
        self.group_name = "persistence_consumers"

    async def publish_event(self, event_type: str, payload: Dict[str, Any]):
        """
        Publishes a new signal to the stream.
        Utilized by the Module 1 Satellites to report new package discoveries.
        """
        event_id = str(uuid.uuid4())
        data = {
            "id": event_id,
            "type": event_type,
            "payload": json.dumps(payload),
            "timestamp": datetime.utcnow().isoformat(),
        }
        # Add to the stream with a max length of 100,000 to prevent memory bloat on the i9 RAM
        await self.client.xadd(self.stream_name, data, maxlen=100000)
        logging.info(f"[EVENT_BUS] Published {event_type} signal: {event_id}")

    async def subscribe(self, callback: Callable[[str, Dict[str, Any]], Awaitable[None]]):
        """
        The i9 Consumer Loop.
        Listens for incoming events and triggers the appropriate DAL updates.
        """
        # Create consumer group if it doesn't exist
        try:
            await self.client.xgroup_create(
                self.stream_name, self.group_name, id="0", mkstream=True
            )
        except redis.exceptions.ResponseError:
            pass  # Group already exists in the current Redis instance

        consumer_id = f"consumer_{os.getpid()}"
        logging.info(f"[EVENT_BUS] Consumer {consumer_id} started on E-cores.")

        while True:
            # Read from the stream (Block for 1 second if empty)
            # Utilizing Consumer Groups ensures that multiple satellites can ingest horizontally
            streams = await self.client.xreadgroup(
                self.group_name, consumer_id, {self.stream_name: ">"}, count=10, block=1000
            )

            if not streams:
                continue

            for stream, messages in streams:
                for message_id, message_data in messages:
                    event_type = message_data["type"]
                    payload = json.loads(message_data["payload"])

                    # Execute the DAL logic (Idempotent Insertion)
                    try:
                        await callback(event_type, payload)
                        # Acknowledge successful processing to Redis
                        await self.client.xack(self.stream_name, self.group_name, message_id)
                    except Exception as e:
                        logging.error(f"[EVENT_BUS] Failed to process event {message_id}: {e}")
                        # Event will be retried (PEL - Pending Entry List) after a timeout


# Global Singleton Accessor
cache_event_bus = EventBus()
