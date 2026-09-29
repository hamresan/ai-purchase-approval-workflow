from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from datetime import timedelta
from uuid import UUID

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
from notification.application.contracts.queue import NotificationQueue
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from ai_purchase_workflow.application.access import ApplicationRole
from ai_purchase_workflow.composition_root.settings import Settings
from ai_purchase_workflow.infrastructure.access import SqlAlchemyRoleWriter
from ai_purchase_workflow.infrastructure.notifications import (
    DevelopmentNotificationQueue,
    InMemoryNotificationQueue,
    UnusedNotificationProviderResolver,
    UnusedNotificationTemplateRenderer,
)
from ai_purchase_workflow.presentation.auth.registration_role_provisioning import (
    RegistrationRoleProvisioningOtpVerifier,
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

    if notification_queue is not None:
        resolved_notification_queue: NotificationQueue = notification_queue
    else:
        in_memory_queue = InMemoryNotificationQueue()
        resolved_notification_queue = (
            DevelopmentNotificationQueue(in_memory_queue)
            if settings.app_env == "development"
            else in_memory_queue
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
    identity = IdentityModule(
        IdentityModuleConfig(
            session_factory=identity_session_factory,
            notification_sender=notification.sender,
            access_token_issuer=issuer,
            access_token_authenticator=authenticator,
            signing_secret=settings.identity_signing_secret.encode(),
        )
    )

    class SessionScopedRoleWriter:
        async def ensure_role(self, user_id: UUID, role: ApplicationRole) -> None:
            async with session_factory() as session:
                await SqlAlchemyRoleWriter(session).ensure_role(user_id, role)

    provisioner = RegistrationRoleProvisioningOtpVerifier(
        verifier=identity.otp_verifier,
        role_writer=SessionScopedRoleWriter(),
    )
    identity.public_api = type(identity.public_api)(
        access_token_authenticator=identity.public_api.access_token_authenticator,
        external_identity_authenticator=identity.public_api.external_identity_authenticator,
        otp_requester=identity.public_api.otp_requester,
        otp_verifier=provisioner,
        session_refresher=identity.public_api.session_refresher,
        session_revoker=identity.public_api.session_revoker,
        session_bulk_revoker=identity.public_api.session_bulk_revoker,
        data_retention_cleaner=identity.public_api.data_retention_cleaner,
    )
    identity.fastapi = type(identity.fastapi)(
        access_token_authenticator=identity.fastapi.access_token_authenticator,
        otp_requester=identity.fastapi.otp_requester,
        otp_verifier=provisioner,
        session_refresher=identity.fastapi.session_refresher,
        session_revoker=identity.fastapi.session_revoker,
        session_bulk_revoker=identity.fastapi.session_bulk_revoker,
        request_metadata_resolver=identity.fastapi.request_metadata_resolver,
    )
    return identity
