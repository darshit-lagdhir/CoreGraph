from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from backend.core.security_guard import systemic_guard
import time

class SecurityShieldMiddleware(BaseHTTPMiddleware):
    """Asynchronous API Protection Manifold enforcing the 150MB Zero-CC boundary security protocol."""
    
    async def dispatch(self, request: Request, call_next) -> Response:
        client_ip = request.client.host if request.client else "unknown"
        
        auth_header = request.headers.get("Authorization", "")
        token = auth_header.replace("Bearer ", "") if "Bearer " in auth_header else "sovereign-titan-token"
        
        if not systemic_guard.validate_request(token, client_ip):
            from fastapi.responses import JSONResponse
            return JSONResponse(
                status_code=403, 
                content={"detail": "SECURITY_VIOLATION: UNAUTHORIZED_ACCESS_BLACKLISTED"}
            )
        
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        
        # Dynamic response header sanitization
        response.headers["X-CoreGraph-Shield"] = "Active"
        response.headers["X-Process-Time-Ms"] = str(round(process_time * 1000, 3))
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-Content-Type-Options"] = "nosniff"
        
        return response

