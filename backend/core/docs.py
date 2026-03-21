import functools
import re
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi


from typing import Dict, Any


def _redact_secrets(schema: Dict[str, Any]) -> None:
    """
    Recursively audits the OpenAPI schema dictionary and redacts any properties
    marked with the 'format': 'password' or associated with SecretStr, ensuring
    high-value API credentials are mathematically prevented from leaking into the
    public technical reference.
    """
    if isinstance(schema, dict):
        # Prevent any SecretStr-related descriptions from displaying their type logic
        if "format" in schema and schema["format"] == "password":
            schema["description"] = "REDACTED: Security Vault Credential."
            if "example" in schema:
                schema["example"] = "********"
        for key, value in schema.items():
            _redact_secrets(value)
    elif isinstance(schema, list):
        for item in schema:
            _redact_secrets(item)


def _correct_uuid_formatting(schema: Dict[str, Any]) -> None:
    """
    Recursively scans the schema to locate any field titled 'id' or ending in '_id' that
    does not correctly define the UUIDv4 format, correcting the type-drift to ensure
    client-side generator compatibility.
    """
    if isinstance(schema, dict):
        if "title" in schema and (
            schema["title"].lower() == "id" or schema["title"].lower().endswith("_id")
        ):
            if schema.get("type") == "string":
                schema["format"] = "uuid"
                schema["pattern"] = (
                    "^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$"
                )
        for key, value in schema.items():
            _correct_uuid_formatting(value)
    elif isinstance(schema, list):
        for item in schema:
            _correct_uuid_formatting(item)


def _inject_websocket_telemetry(openapi_schema: Dict[str, Any]) -> None:
    """
    Manually injects the AsyncAPI-inspired WebSocket telemetry specification
    into the paths object, satisfying the documentation gap for the 64KB chunked,
    zlib-compressed binary protocol.
    """
    websocket_spec = {
        "get": {
            "tags": ["Telemetry"],
            "summary": "Real-Time Binary Telemetry Stream",
            "description": "Establishes a persistent WebSocket connection transmitting 64KB chunked, zlib-compressed binary topology. The client must utilize pako for exact decompression.",
            "responses": {
                "101": {
                    "description": "Switching Protocols - WebSockets",
                    "content": {
                        "application/octet-stream": {
                            "schema": {
                                "type": "string",
                                "format": "binary",
                                "description": "Deflated zlib binary payload mapping structural boundaries.",
                            }
                        }
                    },
                }
            },
        }
    }

    if "paths" not in openapi_schema:
        openapi_schema["paths"] = {}

    openapi_schema["paths"]["/ws/telemetry"] = websocket_spec


def setup_automated_docs(app: FastAPI) -> None:
    """
    Surgically modifies the default FastAPI OpenAPI generator, wrapping the
    calculation in a memoization cache to prevent i9 processor latency spikes.
    """

    @functools.lru_cache(maxsize=1)
    def custom_openapi() -> Dict[str, Any]:
        if app.openapi_schema:
            return dict(app.openapi_schema)

        openapi_schema = get_openapi(
            title="CoreGraph Enterprise Intelligence Gateway",
            version="1.4.0",
            description="""
Hardware-Optimized Intelligence Environment Technical Contract.
Reference Hardware: 24-core i9-13980hx, 16GB RAM. WSL2 limit: 8GB.
            """,
            routes=app.routes,
        )

        openapi_schema["openapi"] = "3.1.0"

        # Enforce Security Redaction
        _redact_secrets(openapi_schema)

        # Correct UUID Formatting Error
        _correct_uuid_formatting(openapi_schema)

        # Inject Missing Protocol Logic
        _inject_websocket_telemetry(openapi_schema)

        # Inject Descriptions into FastAPI Auto-Generated Schemas
        if "components" in openapi_schema and "schemas" in openapi_schema["components"]:
            schemas = openapi_schema["components"]["schemas"]
            if "HTTPValidationError" in schemas:
                for prop_name, prop_data in (
                    schemas["HTTPValidationError"].get("properties", {}).items()
                ):
                    prop_data["description"] = f"HTTP validation error detail: {prop_name}."
            if "ValidationError" in schemas:
                for prop_name, prop_data in (
                    schemas["ValidationError"].get("properties", {}).items()
                ):
                    prop_data["description"] = f"Standard validation error property: {prop_name}."

        app.openapi_schema = openapi_schema
        return dict(app.openapi_schema)

    app.openapi = custom_openapi
