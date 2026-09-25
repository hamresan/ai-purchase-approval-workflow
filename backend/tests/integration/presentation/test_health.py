from typing import cast

from fastapi.testclient import TestClient
from httpx import Response

from ai_purchase_workflow.composition_root.settings import Settings
from ai_purchase_workflow.presentation.app import create_app


def test_health_endpoint_returns_ok() -> None:
    app = create_app(Settings())

    with TestClient(app) as client:
        response = cast(Response, client.get("/health"))

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
