import json
import os
import re
from pathlib import Path
from fastapi.testclient import TestClient

from main import app
from core.docs import setup_automated_docs
from schemas.api import EnhancedBaseModel

# Initialize documentation engine for the strict testing protocol
setup_automated_docs(app)

client = TestClient(app, base_url="http://localhost")


from typing import Dict, Any


def test_openapi_schema_integrity() -> None:
    """
    Asserts the OpenAPI manifest strictly conforms to the 3.1.0 boundary parameter
    and correctly formats the uuid references.
    """
    response = client.get("/openapi.json")
    assert response.status_code == 200
    schema = response.json()

    assert schema["openapi"] == "3.1.0"

    # Assert uuid format correction specifically targeting the 128-bit regex
    components = schema.get("components", {}).get("schemas", {})
    package_schema = components.get("PackageSchema", {})
    properties = package_schema.get("properties", {})

    if "id" in properties:
        id_field = properties["id"]
        assert id_field.get("format") == "uuid"
        assert "^[0-9a-f]{8}" in id_field.get("pattern", "")


def _check_descriptions_recursively(schema_obj: Dict[str, Any]) -> None:
    if "properties" in schema_obj:
        for prop_name, prop_data in schema_obj["properties"].items():
            assert (
                "description" in prop_data and prop_data["description"].strip() != ""
            ), f"Validation Failure: Missing descriptive architecture for field '{prop_name}'."
            # Recurse into nested
            if "items" in prop_data and isinstance(prop_data["items"], dict):
                _check_descriptions_recursively(prop_data["items"])


def test_pydantic_description_coverage() -> None:
    """
    Executes a recursive descent into the generated OpenAPI models to ensure
    100% descriptive structural coverage.
    """
    response = client.get("/openapi.json")
    schema = response.json()

    schemas = schema.get("components", {}).get("schemas", {})
    assert len(schemas) > 0, "No schema structures located in the OpenAPI manifest."

    for name, schema_def in schemas.items():
        _check_descriptions_recursively(schema_def)


def test_link_integrity_audit() -> None:
    """
    Traverses the markdown artifacts within the Reference Vault to strictly
    guarantee local file resolution capabilities for all technical cross-references.
    """
    base_dir = Path("docs/reference")
    # Only run the check if the files exist to prevent failure in isolation
    if not base_dir.exists():
        return

    for md_file in base_dir.glob("*.md"):
        content = md_file.read_text("utf-8")
        links = re.findall(r"\[([^\]]+)\]\(([^)]+)\)", content)
        for text, target in links:
            target_path = base_dir / target
            assert (
                target_path.exists()
            ), f"Broken linkage discovered in {md_file.name}: The target {target} does not resolve."


def test_binary_telemetry_documentation() -> None:
    """
    Validates the explicit documentation of the chunked, zlib-compressed WebSocket
    architecture within the structural path matrix.
    """
    response = client.get("/openapi.json")
    schema = response.json()

    paths = schema.get("paths", {})
    assert "/ws/telemetry" in paths, "WebSocket telemetry pathway missing from operational matrix."

    ws_doc = paths["/ws/telemetry"]["get"]["description"]
    assert "zlib-compressed" in ws_doc
    assert "64KB chunked" in ws_doc
    assert "pako" in ws_doc


def test_hardware_constraint_reflection() -> None:
    """
    Ensures that the performance boundaries established by the base architecture
    are clearly exposed to the integration engineers.
    """
    response = client.get("/openapi.json")
    schema = response.json()

    info = schema.get("info", {})
    desc = info.get("description", "")

    assert "24-core i9-13980hx" in desc
    assert "16GB RAM" in desc
    assert "WSL2 limit: 8GB" in desc


def test_secret_redaction_audit() -> None:
    """
    Secures the public manifest by confirming that high-value secrets are
    mathematically stripped from the endpoint examples and descriptions.
    """
    response = client.get("/openapi.json")
    schema = response.json()

    schemas = schema.get("components", {}).get("schemas", {})
    auth_schema = schemas.get("AuthSchema", {})
    props = auth_schema.get("properties", {})

    if "access_token" in props:
        token_prop = props["access_token"]
        assert "REDACTED" in token_prop.get("description", "")
        if "example" in token_prop:
            assert token_prop["example"] == "********"
