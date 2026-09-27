from decimal import Decimal

import pytest

from ai_purchase_workflow.application.purchase_requests import GetPurchaseRequestDetail
from ai_purchase_workflow.application.purchase_requests.repository import PurchaseRequestRepository
from ai_purchase_workflow.domain.purchase_requests import (
    AuditEntry,
    DraftOrder,
    Money,
    PurchaseItem,
    PurchaseRequest,
)


@pytest.mark.asyncio
async def test_get_purchase_request_detail_maps_trusted_aggregate(
    repository: PurchaseRequestRepository,
) -> None:
    item = PurchaseItem("Laptop stand", 2, Money(Decimal("35.00"), "USD"), "Acme")
    request = PurchaseRequest.create((item,), requester_name="Dana")
    request.draft_order = DraftOrder.create(request.id, (item,), Money(Decimal("70.00"), "USD"))
    request.audit_entries = (
        AuditEntry.create(
            request.id,
            "trusted_data_validated",
            "Vendor availability, draft order, and budget policy checks passed.",
        ),
    )
    await repository.add(request)

    detail = await GetPurchaseRequestDetail(repository).execute(request.id)

    assert detail.id == request.id
    assert detail.budget_outcome == "passed"
    assert detail.draft_order is not None
    assert detail.draft_order.total_amount == Decimal("70.00")
    assert detail.items[0].vendor == "Acme"
    assert detail.audit_entries[0].event_type == "trusted_data_validated"
