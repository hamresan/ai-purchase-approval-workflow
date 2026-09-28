from httpx import ASGITransport, AsyncClient
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from ai_purchase_workflow.application.access import ApplicationRole
from ai_purchase_workflow.composition_root.settings import Settings
from ai_purchase_workflow.infrastructure.access import ApplicationUserRoleModel
from ai_purchase_workflow.infrastructure.notifications import InMemoryNotificationQueue
from ai_purchase_workflow.presentation.app import create_app


async def test_identity_otp_request_queues_notification(
    session_factory: async_sessionmaker[AsyncSession],
    test_database_url: str,
) -> None:
    settings = Settings(database_url=test_database_url)
    queue = InMemoryNotificationQueue()
    app = create_app(settings, notification_queue=queue)
    app.state.session_factory = session_factory

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


async def test_registered_identity_with_requester_role_can_access_purchase_api(
    session_factory: async_sessionmaker[AsyncSession],
    test_database_url: str,
) -> None:
    settings = Settings(database_url=test_database_url)
    queue = InMemoryNotificationQueue()
    app = create_app(settings, notification_queue=queue)
    app.state.session_factory = session_factory

    async with (
        app.router.lifespan_context(app),
        AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client,
    ):
        otp_response = await client.post(
            "/identity/otp/request",
            json={
                "identity_type": "mobile",
                "destination": "+96890000001",
                "purpose": "registration",
                "locale": "en",
            },
        )
        assert otp_response.status_code == 202
        otp = queue.items[0].variables["otp"]
        assert isinstance(otp, str)

        verify_response = await client.post(
            "/identity/otp/verify",
            json={
                "challenge_id": otp_response.json()["challenge_id"],
                "code": otp,
                "full_name": "Dana",
            },
        )
        assert verify_response.status_code == 200
        auth_session = verify_response.json()

        async with session_factory() as session:
            session.add(
                ApplicationUserRoleModel(
                    user_id=UUID(auth_session["user_id"]),
                    role=ApplicationRole.REQUESTER.value,
                )
            )
            await session.commit()

        response = await client.get(
            "/api/purchase-requests",
            headers={"Authorization": f"Bearer {auth_session['access_token']}"},
        )

    assert response.status_code == 200
