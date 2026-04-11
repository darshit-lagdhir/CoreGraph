import logging
import uuid

from core.logging_config import correlation_id_var
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)

class TraceMiddleware(BaseHTTPMiddleware):
    """Entry-point Telemetry: Enforces Trace Correlation across the ASGI Gateway."""

    async def dispatch(self, request: Request, call_next):
        # 1. Capture Header or Generate UUID (Gateway Interception)
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))

        # 2. Context Initialization: Local to this asynchronous execution loop
        token = correlation_id_var.set(request_id)

        try:
            response: Response = await call_next(request)
            # Propagate back to OSINT operator
            response.headers["X-Request-ID"] = request_id
            return response
        except Exception as e:
            logger.error(f"Global trace failure, rectifying: {str(e)}", exc_info=True)
            return JSONResponse(
                status_code=500,
                content={"error": "Asynchronous Kernel Failure", "detail": "Internal logic exception intercepted."},
                headers={"X-Request-ID": request_id}
            )
        finally:
            # Token clearing to prevent context leakage between requests
            correlation_id_var.reset(token)
