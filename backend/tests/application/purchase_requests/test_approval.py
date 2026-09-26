from decimal import Decimal

import pytest

from ai_purchase_workflow.application.purchase_requests.approval import (
    ApprovePurchaseRequest,
    EditPurchaseItem,
    EditPurchaseRequest,
    RejectPurchaseRequest,
)
from ai_purchase_workflow.application.purchase_requests.trusted_tools import (
    CheckBudget,
    CreateDraftOrder,
    FindVendor,
)
from ai_purchase_workflow.domain.purchase_requests import (
    BudgetPolicy,
    DraftOrderPolicy,
    Money,
    PurchaseItem,
    PurchaseRequest,
    RequestStatus,
    VendorPolicy,
)
from tests.application.purchase_requests.fakes import (
    FakeBudgetReader,
    FakeCatalogReader,
    FakePurchaseRequestWorkflowGateway,
    InMemoryPurchaseRequestRepository,
)


async def make_pending_request(
    repository: InMemoryPurchaseRequestRepository,
) -> PurchaseRequest:
    request = PurchaseRequest.create(
        (PurchaseItem("Laptop stand", 1, Money(Decimal("35.00"), "USD"), "Acme"),),
        requester_name="Dana",
    )
    request.draft_order = CreateDraftOrder(DraftOrderPolicy()).execute(request, request.items)
    request.transition_to(RequestStatus.PENDING_APPROVAL)
    await repository.add(request)
    return request


@pytest.mark.asyncio
async def test_approve_records_decision_and_resumes_workflow() -> None:
    repository = InMemoryPurchaseRequestRepository()
    workflow = FakePurchaseRequestWorkflowGateway()
    request = await make_pending_request(repository)

    view = await ApprovePurchaseRequest(repository, workflow).execute(
        request.id,
        decided_by="Manager",
        reason="Within policy",
    )

    assert view.status is RequestStatus.APPROVED
    assert workflow.approved_request_ids == [request.id]
    stored = await repository.get(request.id)
    assert stored is not None
    assert stored.approval_decision is not None
    assert stored.audit_entries[-1].event_type == "approval_approved"


@pytest.mark.asyncio
async def test_duplicate_approval_does_not_resume_workflow_twice() -> None:
    repository = InMemoryPurchaseRequestRepository()
    workflow = FakePurchaseRequestWorkflowGateway()
    request = await make_pending_request(repository)
    use_case = ApprovePurchaseRequest(repository, workflow)

    await use_case.execute(request.id, decided_by="Manager")
    await use_case.execute(request.id, decided_by="Manager")

    assert workflow.approved_request_ids == [request.id]


@pytest.mark.asyncio
async def test_reject_records_decision_without_approval_resume() -> None:
    repository = InMemoryPurchaseRequestRepository()
    workflow = FakePurchaseRequestWorkflowGateway()
    request = await make_pending_request(repository)

    view = await RejectPurchaseRequest(repository, workflow).execute(
        request.id,
        decided_by="Manager",
        reason="Not required",
    )

    assert view.status is RequestStatus.REJECTED
    assert workflow.rejected_request_ids == [request.id]
    assert workflow.approved_request_ids == []


@pytest.mark.asyncio
async def test_edit_revalidates_against_trusted_sources_and_stays_pending() -> None:
    repository = InMemoryPurchaseRequestRepository()
    request = await make_pending_request(repository)
    use_case = EditPurchaseRequest(
        repository=repository,
        find_vendor=FindVendor(FakeCatalogReader(), VendorPolicy()),
        create_draft_order=CreateDraftOrder(DraftOrderPolicy()),
        check_budget=CheckBudget(FakeBudgetReader(), BudgetPolicy()),
    )

    view = await use_case.execute(
        request.id,
        items=(EditPurchaseItem("Monitor", 1),),
        decided_by="Manager",
    )

    assert view.status is RequestStatus.PENDING_APPROVAL
    stored = await repository.get(request.id)
    assert stored is not None
    assert stored.items[0].description == "Monitor"
    assert stored.items[0].vendor == "Trusted Vendor"
    assert stored.items[0].unit_price.amount == Decimal("25.00")
    assert stored.draft_order is not None
    assert stored.audit_entries[-1].event_type == "approval_edited"
    assert "Manager" in stored.audit_entries[-1].message
