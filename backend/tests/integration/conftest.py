import os
from collections.abc import AsyncIterator

import pytest
from alembic import command
from alembic.config import Config
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from tests.application.purchase_requests.fakes.workflow import FakePurchaseRequestWorkflowGateway

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
from ai_purchase_workflow.presentation.purchase_requests.approval_dispatcher import (
    ApprovalActionDispatcher,
    ApproveActionHandler,
    EditActionHandler,
    RejectActionHandler,
)
from ai_purchase_workflow.presentation.purchase_requests.dependencies import get_approval_dispatcher

TEST_DATABASE_URL = os.environ["TEST_DATABASE_URL"]


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
                "TRUNCATE workflow_threads, audit_entries, approval_decisions, draft_orders, "
                "purchase_requests RESTART IDENTITY CASCADE"
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
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
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
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client
