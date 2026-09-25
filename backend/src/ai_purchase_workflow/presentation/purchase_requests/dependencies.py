from collections.abc import AsyncIterator
from typing import Annotated

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from ai_purchase_workflow.application.purchase_requests import (
    CreatePurchaseRequest,
    GetPurchaseRequest,
    ListPurchaseRequests,
)
from ai_purchase_workflow.infrastructure.persistence.purchase_requests import (
    SqlAlchemyPurchaseRequestRepository,
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
