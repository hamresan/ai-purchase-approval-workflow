from collections.abc import AsyncIterator
from typing import Annotated

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from ai_purchase_workflow.application.purchase_requests import (
    CreatePurchaseRequest,
    GetPurchaseRequest,
    ListPurchaseRequests,
    PreparePurchaseRequest,
    SubmitPurchaseRequest,
)
from ai_purchase_workflow.composition_root.purchase_requests import (
    build_approve_purchase_request,
    build_edit_purchase_request,
    build_prepare_purchase_request,
    build_reject_purchase_request,
    build_submit_purchase_request,
)
from ai_purchase_workflow.composition_root.workflows import build_workflow_gateway
from ai_purchase_workflow.infrastructure.persistence.purchase_requests import (
    SqlAlchemyPurchaseRequestRepository,
)
from ai_purchase_workflow.infrastructure.persistence.workflow_threads import (
    SqlAlchemyWorkflowThreadRepository,
)
from ai_purchase_workflow.presentation.purchase_requests.approval_dispatcher import (
    ApprovalActionDispatcher,
    ApproveActionHandler,
    EditActionHandler,
    RejectActionHandler,
)


async def get_session(request: Request) -> AsyncIterator[AsyncSession]:
    session_factory = request.app.state.session_factory
    async with session_factory() as session:
        yield session


SessionDependency = Annotated[AsyncSession, Depends(get_session)]


def get_create_purchase_request(session: SessionDependency) -> CreatePurchaseRequest:
    return CreatePurchaseRequest(SqlAlchemyPurchaseRequestRepository(session))


def get_purchase_request(session: SessionDependency) -> GetPurchaseRequest:
    return GetPurchaseRequest(SqlAlchemyPurchaseRequestRepository(session))


def get_list_purchase_requests(session: SessionDependency) -> ListPurchaseRequests:
    return ListPurchaseRequests(SqlAlchemyPurchaseRequestRepository(session))


def get_prepare_purchase_request(session: SessionDependency) -> PreparePurchaseRequest:
    repository = SqlAlchemyPurchaseRequestRepository(session)
    return build_prepare_purchase_request(repository)


def get_submit_purchase_request(session: SessionDependency) -> SubmitPurchaseRequest:
    repository = SqlAlchemyPurchaseRequestRepository(session)
    return build_submit_purchase_request(repository)


def get_approval_dispatcher(
    request: Request,
    session: SessionDependency,
) -> ApprovalActionDispatcher:
    repository = SqlAlchemyPurchaseRequestRepository(session)
    threads = SqlAlchemyWorkflowThreadRepository(session)
    workflow = build_workflow_gateway(
        repository,
        threads,
        request.app.state.checkpointer,
    )
    return ApprovalActionDispatcher(
        ApproveActionHandler(build_approve_purchase_request(repository, workflow)),
        RejectActionHandler(build_reject_purchase_request(repository, workflow)),
        EditActionHandler(build_edit_purchase_request(repository)),
    )
