from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from datetime import timedelta

from identity import IdentityModule, IdentityModuleConfig
from identity.access_tokens import (
    JwtAccessTokenAuthenticator,
    JwtAccessTokenIssuer,
    PyJwtHmacCodec,
    SqlAlchemySessionReader,
    SqlAlchemyUserReader,
    UserStatusPolicy,
)
from identity.infrastructure.security import SystemClock
from notification import NotificationModule, NotificationModuleConfig
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from ai_purchase_workflow.composition_root.settings import Settings
from ai_purchase_workflow.infrastructure.notifications import (
    InMemoryNotificationQueue,
    UnusedNotificationProviderResolver,
    UnusedNotificationTemplateRenderer,
)


def build_identity_module(
    settings: Settings,
    session_factory: async_sessionmaker[AsyncSession],
    *,
    notification_queue: InMemoryNotificationQueue | None = None,
) -> IdentityModule:
    @asynccontextmanager
    async def identity_session_factory() -> AsyncGenerator[AsyncSession]:
        async with session_factory() as session:
            yield session

    resolved_notification_queue = (
        notification_queue
        if notification_queue is not None
        else InMemoryNotificationQueue()
    )
    notification = NotificationModule(
        NotificationModuleConfig(
            queue=resolved_notification_queue,
            renderer=UnusedNotificationTemplateRenderer(),
            provider_resolver=UnusedNotificationProviderResolver(),
        )
    )
    clock = SystemClock()
    codec = PyJwtHmacCodec(secret=settings.identity_jwt_signing_secret)
    issuer = JwtAccessTokenIssuer(
        signer=codec,
        clock=clock,
        ttl=timedelta(minutes=settings.identity_access_token_minutes),
    )
    authenticator = JwtAccessTokenAuthenticator(
        verifier=codec,
        session_reader=SqlAlchemySessionReader(identity_session_factory),
        user_reader=SqlAlchemyUserReader(identity_session_factory),
        user_status_policy=UserStatusPolicy(),
        clock=clock,
    )
    return IdentityModule(
        IdentityModuleConfig(
            session_factory=identity_session_factory,
            notification_sender=notification.sender,
            access_token_issuer=issuer,
            access_token_authenticator=authenticator,
            signing_secret=settings.identity_signing_secret.encode(),
        )
    )
