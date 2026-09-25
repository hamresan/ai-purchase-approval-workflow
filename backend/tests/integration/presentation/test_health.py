from httpx import ASGITransport, AsyncClient
import pytest

from ai_purchase_workflow.composition_root.settings import Settings
from ai_purchase_workflow.presentation.app import create_app


@pytest.mark.asyncio
async def test_health_endpoint_returns_ok() -> None:
    app = create_app(Settings())
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
