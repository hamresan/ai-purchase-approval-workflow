from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from ai_purchase_workflow.composition_root.settings import Settings
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

        response = await client.get(
            "/api/purchase-requests",
            headers={"Authorization": f"Bearer {auth_session['access_token']}"},
        )

    assert response.status_code == 200


async def test_login_does_not_provision_requester_role(
    session_factory: async_sessionmaker[AsyncSession],
    test_database_url: str,
) -> None:
    settings = Settings(database_url=test_database_url)
    queue = InMemoryNotificationQueue()
    app = create_app(settings, notification_queue=queue)
    app.state.session_factory = session_factory
    destination = "+96890000002"

    async with (
        app.router.lifespan_context(app),
        AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client,
    ):
        registration = await client.post(
            "/identity/otp/request",
            json={
                "identity_type": "mobile",
                "destination": destination,
                "purpose": "registration",
                "locale": "en",
            },
        )
        registration_otp = queue.items[-1].variables["otp"]
        assert isinstance(registration_otp, str)
        registered = await client.post(
            "/identity/otp/verify",
            json={
                "challenge_id": registration.json()["challenge_id"],
                "code": registration_otp,
                "full_name": "Dana",
            },
        )
        assert registered.status_code == 200
        user_id = registered.json()["user_id"]

        async with session_factory() as session:
            await session.execute(
                text("DELETE FROM application_user_roles WHERE user_id = :user_id"),
                {"user_id": user_id},
            )
            await session.commit()

        login = await client.post(
            "/identity/otp/request",
            json={
                "identity_type": "mobile",
                "destination": destination,
                "purpose": "login",
                "locale": "en",
            },
        )
        login_otp = queue.items[-1].variables["otp"]
        assert isinstance(login_otp, str)
        verified_login = await client.post(
            "/identity/otp/verify",
            json={
                "challenge_id": login.json()["challenge_id"],
                "code": login_otp,
                "full_name": "Ignored Login Name",
            },
        )
        assert verified_login.status_code == 200

        response = await client.get(
            "/api/purchase-requests",
            headers={"Authorization": f"Bearer {verified_login.json()['access_token']}"},
        )

    assert response.status_code == 403
