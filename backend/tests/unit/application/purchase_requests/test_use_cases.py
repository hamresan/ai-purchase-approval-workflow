from decimal import Decimal
from uuid import uuid4

import pytest
from tests.application.purchase_requests.fakes.idempotency import (
    InMemoryIdempotentPurchaseRequestCreator,
)

from ai_purchase_workflow.application.purchase_requests import (
    CreatePurchaseItem,
    CreatePurchaseRequest,
    CreatePurchaseRequestCommand,
    GetPurchaseRequest,
    ListPurchaseRequests,
    PurchaseRequestListQuery,
)
from ai_purchase_workflow.application.purchase_requests.repository import (
    PurchaseRequestRepository,
)
from ai_purchase_workflow.application.purchase_requests.use_cases import (
    PurchaseRequestNotFoundError,
)
from ai_purchase_workflow.domain.purchase_requests import RequestStatus


@pytest.mark.asyncio
async def test_create_get_and_list_purchase_requests(
    repository: PurchaseRequestRepository,
) -> None:
    create = CreatePurchaseRequest(repository, InMemoryIdempotentPurchaseRequestCreator())
    get = GetPurchaseRequest(repository)
    list_requests = ListPurchaseRequests(repository)
    command = CreatePurchaseRequestCommand(
        requester_name="Sam",
        items=(CreatePurchaseItem("Keyboard", 1, Decimal("89.99"), "usd", "Acme"),),
    )

    created = await create.execute(command)
    retrieved = await get.execute(created.id)
    listed = await list_requests.execute(PurchaseRequestListQuery(status=RequestStatus.DRAFTING))

    assert retrieved == created
    assert listed.items == (created,)
    assert listed.total == 1


@pytest.mark.asyncio
async def test_get_purchase_request_raises_for_unknown_id(
    repository: PurchaseRequestRepository,
) -> None:
    with pytest.raises(PurchaseRequestNotFoundError):
        await GetPurchaseRequest(repository).execute(uuid4())
