from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from uuid import UUID

from fastapi import FastAPI

from ai_purchase_workflow.application.access import ApplicationPrincipal, ApplicationRole
from ai_purchase_workflow.composition_root.identity import build_identity_module
from ai_purchase_workflow.composition_root.settings import Settings, get_settings
from ai_purchase_workflow.infrastructure.notifications import InMemoryNotificationQueue
from ai_purchase_workflow.infrastructure.persistence import create_session_factory
from ai_purchase_workflow.infrastructure.workflows import postgres_checkpointer
from ai_purchase_workflow.presentation.auth import build_profile_router
from ai_purchase_workflow.presentation.observability import register_http_observability
from ai_purchase_workflow.presentation.purchase_requests import router as purchase_requests_router
from ai_purchase_workflow.presentation.purchase_requests.error_handlers import (
    register_purchase_request_error_handlers,
)
from ai_purchase_workflow.presentation.routes import health_router


def create_app(
    settings: Settings | None = None,
    *,
    notification_queue: InMemoryNotificationQueue | None = None,
) -> FastAPI:
    resolved_settings = settings or get_settings()
    session_factory = create_session_factory(resolved_settings.database_url)
    identity = build_identity_module(
        resolved_settings,
        session_factory,
        notification_queue=notification_queue,
    )

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
        async with postgres_checkpointer(resolved_settings.database_url) as checkpointer:
            app.state.checkpointer = checkpointer
            yield

    app = FastAPI(title="AI Purchase Approval Workflow", lifespan=lifespan)
    app.state.settings = resolved_settings
    app.state.session_factory = session_factory
    app.state.identity = identity
    if resolved_settings.app_env == "test":
        app.state.e2e_principals = {
            "requester": ApplicationPrincipal(
                user_id=UUID("11111111-1111-1111-1111-111111111111"),
                session_id=UUID("33333333-3333-3333-3333-333333333333"),
                display_name="Dana",
                roles=frozenset({ApplicationRole.REQUESTER}),
            ),
            "approver": ApplicationPrincipal(
                user_id=UUID("22222222-2222-2222-2222-222222222222"),
                session_id=UUID("44444444-4444-4444-4444-444444444444"),
                display_name="Alex",
                roles=frozenset({ApplicationRole.APPROVER}),
            ),
            "admin": ApplicationPrincipal(
                user_id=UUID("55555555-5555-5555-5555-555555555555"),
                session_id=UUID("66666666-6666-6666-6666-666666666666"),
                display_name="Admin",
                roles=frozenset({ApplicationRole.ADMIN}),
            ),
        }
        app.state.e2e_principal = app.state.e2e_principals["admin"]
    register_http_observability(app)
    register_purchase_request_error_handlers(app)
    identity.fastapi.install(app)
    app.include_router(health_router)
    app.include_router(build_profile_router())
    app.include_router(purchase_requests_router)
    return app
