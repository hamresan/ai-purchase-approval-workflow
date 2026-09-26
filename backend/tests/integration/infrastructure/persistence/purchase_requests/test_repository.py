from decimal import Decimal

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from ai_purchase_workflow.domain.purchase_requests import (
    Money,
    PurchaseItem,
    PurchaseRequest,
    RequestStatus,
)
from ai_purchase_workflow.infrastructure.persistence.purchase_requests import (
    SqlAlchemyPurchaseRequestRepository,
)


@pytest.mark.asyncio
async def test_repository_persists_gets_and_filters_requests(db_session: AsyncSession) -> None:
    repository = SqlAlchemyPurchaseRequestRepository(db_session)
    drafting = PurchaseRequest.create(
        items=(PurchaseItem("Monitor", 1, Money(Decimal("250"), "USD")),),
        requester_name="Alex",
    )
    pending = PurchaseRequest.create(
        items=(PurchaseItem("Keyboard", 2, Money(Decimal("50"), "USD")),),
        requester_name="Sam",
    )
    pending.transition_to(RequestStatus.PENDING_APPROVAL)

    await repository.add(drafting)
    await repository.add(pending)

    loaded = await repository.get(drafting.id)
    filtered = await repository.list_page(
        status=RequestStatus.PENDING_APPROVAL,
        limit=20,
        offset=0,
        descending=False,
    )

    assert loaded is not None
    assert loaded.id == drafting.id
    assert loaded.items == drafting.items
    assert [request.id for request in filtered.items] == [pending.id]
    assert filtered.total == 1
