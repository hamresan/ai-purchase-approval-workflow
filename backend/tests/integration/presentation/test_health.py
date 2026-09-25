from fastapi.testclient import TestClient

from ai_purchase_workflow.composition_root.settings import Settings
from ai_purchase_workflow.presentation.app import create_app


def test_health_endpoint_returns_ok() -> None:
    app = create_app(Settings(_env_file=None))
    with TestClient(app) as client:
        response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
