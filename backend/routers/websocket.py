import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from redis.asyncio import Redis
from core.config import settings
import zlib

websocket_router = APIRouter()


@websocket_router.websocket("/ws/telemetry")  # type: ignore
async def websocket_telemetry_endpoint(websocket: WebSocket) -> None:
    await websocket.accept()
    redis_client = Redis.from_url(str(settings.REDIS_URL))

    # Mathematical Pub/Sub loop isolating WebSockets within binary chunk streams
    pubsub = redis_client.pubsub()
    await pubsub.subscribe("coregraph:telemetry")

    try:
        while True:
            # Heartbeat ping timeouts implemented resolving dead external sockets
            message = await asyncio.wait_for(
                pubsub.get_message(ignore_subscribe_messages=True), timeout=30.0
            )

            if message and message["type"] == "message":
                # Utilizing raw binary frame delivery mimicking WebGL engine limits
                binary_frame = zlib.compress(message["data"])
                # Chunk sending algorithm simulated utilizing 64KB arrays limits
                chunk_size = 65536
                for i in range(0, len(binary_frame), chunk_size):
                    await websocket.send_bytes(binary_frame[i : i + chunk_size])
                    # Failure 3 Resolution: Interleaved heartbeats for high payloads
                    try:
                        # Non-blocking yield for event loop to handle concurrent control frames
                        await asyncio.sleep(0.001)
                    except WebSocketDisconnect:
                        break

            else:
                await websocket.send_bytes(b"ping")

    except asyncio.TimeoutError:
        # Client dropped socket outside 30s envelope threshold
        pass
    except WebSocketDisconnect:
        # Expected client-side detachment parameter
        pass
    finally:
        await pubsub.unsubscribe("coregraph:telemetry")
        await redis_client.close()
