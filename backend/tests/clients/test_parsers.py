import pytest
import respx
import httpx
from typing import Any
from clients.ecosystems import EcosystemFactory, PyPIClient, GoClient


@pytest.mark.asyncio
async def test_pypi_normalization_drift() -> None:
    # Failure 1 Logic: Asserting case-sensitivity and hyphen equivalence
    async with httpx.AsyncClient() as client:
        pypi = PyPIClient(client)

        name1 = "Flask-SQLAlchemy"
        name2 = "flask_sqlalchemy"

        norm1 = pypi.normalize_package_name(name1)
        norm2 = pypi.normalize_package_name(name2)

        assert norm1 == norm2
        assert norm1 == "flask-sqlalchemy"


@pytest.mark.asyncio
async def test_go_pseudo_version_parsing() -> None:
    # Failure 2 Logic: Asserting resilient regex for pseudo-versions
    async with httpx.AsyncClient() as client:
        go = GoClient(client)

        v1 = "v0.0.0-20190718012654-fb15b899a751"
        v2 = "v1.2.3"

        clean1 = go.normalize_version(v1)
        clean2 = go.normalize_version(v2)

        assert clean1 == "0.0.0"
        assert clean2 == "1.2.3"


@pytest.mark.asyncio
@respx.mock
async def test_multi_ecosystem_factory_instantiation() -> None:
    async with httpx.AsyncClient() as client:
        pypi_client = EcosystemFactory.get_client("pypi", client)
        go_client = EcosystemFactory.get_client("go", client)

        assert isinstance(pypi_client, PyPIClient)
        assert isinstance(go_client, GoClient)

        with pytest.raises(ValueError):
            EcosystemFactory.get_client("invalid", client)


@pytest.mark.asyncio
@respx.mock
async def test_pypi_metadata_ingestion(respx_mock: Any) -> None:
    async with httpx.AsyncClient() as client:
        pypi = PyPIClient(client)

        # Mocking PyPI JSON API
        url = "https://pypi.org/pypi/requests/json"
        respx_mock.get(url).respond(
            json={
                "info": {
                    "name": "requests",
                    "version": "2.28.1",
                    "requires_dist": ["urllib3 (>=1.21.1)", "certifi (>=2017.4.17)"],
                }
            }
        )

        metadata = await pypi.fetch_metadata("requests")
        deps = pypi.resolve_dependencies(metadata)

        assert len(deps) == 2
        assert deps[0].name == "urllib3"
        assert deps[0].version_range == ">=1.21.1"
        assert deps[0].ecosystem == "pypi"
