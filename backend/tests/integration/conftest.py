import os
from uuid import UUID
from collections.abc import AsyncIterator

import pytest
from alembic import command
from alembic.config import Config
from fastapi import Request
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from tests.application.purchase_requests.fakes.workflow import FakePurchaseRequestWorkflowGateway

from ai_purchase_workflow.application.access import ApplicationPrincipal, ApplicationRole
from ai_purchase_workflow.composition_root.purchase_requests import (
    build_approve_purchase_request,
    build_edit_purchase_request,
    build_reject_purchase_request,
)
from ai_purchase_workflow.composition_root.settings import Settings
from ai_purchase_workflow.infrastructure.persistence.purchase_requests import (
    SqlAlchemyPurchaseRequestRepository,
)
from ai_purchase_workflow.presentation.app import create_app
from ai_purchase_workflow.presentation.auth.dependencies import get_current_principal
from ai_purchase_workflow.presentation.purchase_requests.approval_dispatcher import (
    ApprovalActionDispatcher,
    ApproveActionHandler,
    EditActionHandler,
    RejectActionHandler,
)
from ai_purchase_workflow.presentation.purchase_requests.dependencies import get_approval_dispatcher

TEST_DATABASE_URL = os.environ["TEST_DATABASE_URL"]
TEST_REQUESTER_ID = UUID("11111111-1111-1111-1111-111111111111")
TEST_APPROVER_ID = UUID("22222222-2222-2222-2222-222222222222")
TEST_SESSION_ID = UUID("33333333-3333-3333-3333-333333333333")


async def requester_principal() -> ApplicationPrincipal:
    return ApplicationPrincipal(
        user_id=TEST_REQUESTER_ID,
        session_id=TEST_SESSION_ID,
        display_name="Dana",
        roles=frozenset({ApplicationRole.REQUESTER}),
    )


async def approver_principal() -> ApplicationPrincipal:
    return ApplicationPrincipal(
        user_id=TEST_APPROVER_ID,
        session_id=TEST_SESSION_ID,
        display_name="Manager",
        roles=frozenset({ApplicationRole.APPROVER}),
    )



@pytest.fixture(scope="session", autouse=True)
def migrate_database() -> None:
    config = Config("alembic.ini")
    config.set_main_option("sqlalchemy.url", TEST_DATABASE_URL)
    command.upgrade(config, "head")


@pytest.fixture(scope="session")
def test_database_url() -> str:
    return TEST_DATABASE_URL


@pytest.fixture
async def session_factory() -> AsyncIterator[async_sessionmaker[AsyncSession]]:
    engine = create_async_engine(TEST_DATABASE_URL)
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as session:
        await session.execute(
            text(
                "TRUNCATE purchase_request_idempotency, workflow_threads, audit_entries, "
                "approval_decisions, draft_orders, purchase_requests RESTART IDENTITY CASCADE"
            )
        )
        await session.commit()
    yield factory
    await engine.dispose()


@pytest.fixture
async def db_session(
    session_factory: async_sessionmaker[AsyncSession],
) -> AsyncIterator[AsyncSession]:
    async with session_factory() as session:
        yield session


@pytest.fixture
async def api_client(
    session_factory: async_sessionmaker[AsyncSession],
) -> AsyncIterator[AsyncClient]:
    app = create_app(Settings(database_url=TEST_DATABASE_URL))
    app.state.session_factory = session_factory
    app.dependency_overrides[get_current_principal] = requester_principal
    async with (
        app.router.lifespan_context(app),
        AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client,
    ):
        yield client


@pytest.fixture
async def approval_api_client(
    session_factory: async_sessionmaker[AsyncSession],
) -> AsyncIterator[AsyncClient]:
    app = create_app(Settings(database_url=TEST_DATABASE_URL))
    app.state.session_factory = session_factory
    workflow = FakePurchaseRequestWorkflowGateway()

    async def override_approval_dispatcher() -> AsyncIterator[ApprovalActionDispatcher]:
        async with session_factory() as session:
            repository = SqlAlchemyPurchaseRequestRepository(session)
            yield ApprovalActionDispatcher(
                ApproveActionHandler(build_approve_purchase_request(repository, workflow)),
                RejectActionHandler(build_reject_purchase_request(repository, workflow)),
                EditActionHandler(build_edit_purchase_request(repository)),
            )

    app.dependency_overrides[get_approval_dispatcher] = override_approval_dispatcher

    async def request_aware_principal(request: Request) -> ApplicationPrincipal:
        if request.url.path.endswith("/approval"):
            return await approver_principal()
        return await requester_principal()

    app.dependency_overrides[get_current_principal] = request_aware_principal
    async with (
        app.router.lifespan_context(app),
        AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client,
    ):
        yield client
