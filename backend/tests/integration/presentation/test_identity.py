from httpx import ASGITransport, AsyncClient

from ai_purchase_workflow.composition_root.identity import build_identity_module
from ai_purchase_workflow.composition_root.settings import Settings
from ai_purchase_workflow.infrastructure.notifications import InMemoryNotificationQueue
from ai_purchase_workflow.presentation.app import create_app


async def test_identity_otp_request_queues_notification(
    session_factory,
    test_database_url: str,
) -> None:
    settings = Settings(database_url=test_database_url)
    queue = InMemoryNotificationQueue()
    app = create_app(settings)
    app.state.session_factory = session_factory
    app.state.identity = build_identity_module(
        settings,
        session_factory,
        notification_queue=queue,
    )

    async with (
        app.router.lifespan_context(app),
        AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client,
    ):
        response = await client.post(
            "/identity/otp/request",
            json={
                "identity_type": "mobile",
                "destination": "+96890000000",
                "purpose": "registration",
                "locale": "en",
            },
        )

    assert response.status_code == 202
    assert len(queue.items) == 1
    notification = queue.items[0]
    assert notification.recipient == "+96890000000"
    assert notification.template_key == "identity.otp"
    assert notification.locale == "en"
    assert notification.variables["purpose"] == "registration"
    assert isinstance(notification.variables["otp"], str)
    assert notification.variables["otp"]
