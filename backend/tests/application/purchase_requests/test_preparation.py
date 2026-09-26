from decimal import Decimal

import pytest

from ai_purchase_workflow.application.purchase_requests import PurchaseRequestRepository
from ai_purchase_workflow.application.purchase_requests.preparation import (
    PreparePurchaseRequest,
    SubmitPurchaseRequest,
)
from ai_purchase_workflow.application.purchase_requests.trusted_tools import (
    CheckBudget,
    CreateDraftOrder,
    FindVendor,
    SubmitOrder,
)
from ai_purchase_workflow.domain.purchase_requests import (
    ApprovalDecision,
    ApprovalGatePolicy,
    ApprovalOutcome,
    BudgetPolicy,
    DomainValidationError,
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
    FakeOrderGateway,
)


async def test_prepare_purchase_request_builds_trusted_draft_and_moves_to_pending(
    repository: PurchaseRequestRepository,
) -> None:
    request = PurchaseRequest.create(
        (
            PurchaseItem(
                "Laptop stand",
                2,
                Money(Decimal("999.00"), "USD"),
                "Untrusted Vendor",
            ),
        ),
        requester_name="Dana",
    )
    await repository.add(request)
    use_case = PreparePurchaseRequest(
        repository,
        FindVendor(FakeCatalogReader(), VendorPolicy()),
        CreateDraftOrder(DraftOrderPolicy()),
        CheckBudget(FakeBudgetReader(), BudgetPolicy()),
    )

    view = await use_case.execute(request.id)
    stored = await repository.get(request.id)

    assert view.status is RequestStatus.PENDING_APPROVAL
    assert stored is not None
    assert stored.draft_order is not None
    assert stored.draft_order.items[0].vendor == "Trusted Vendor"
    assert stored.draft_order.total.amount == Decimal("50.00")
    assert [entry.event_type for entry in stored.audit_entries] == [
        "trusted_data_validated",
        "approval_paused",
    ]


async def test_prepare_purchase_request_rejects_missing_budget_data(
    repository: PurchaseRequestRepository,
) -> None:
    request = PurchaseRequest.create((PurchaseItem("Laptop stand", 1, Money(Decimal("1"), "USD")),))
    await repository.add(request)
    use_case = PreparePurchaseRequest(
        repository,
        FindVendor(FakeCatalogReader(), VendorPolicy()),
        CreateDraftOrder(DraftOrderPolicy()),
        CheckBudget(FakeBudgetReader(), BudgetPolicy()),
    )

    with pytest.raises(DomainValidationError, match="budget data"):
        await use_case.execute(request.id)


async def test_submit_purchase_request_rejects_preapproval_at_application_boundary(
    repository: PurchaseRequestRepository,
) -> None:
    request = PurchaseRequest.create(
        (PurchaseItem("Laptop stand", 1, Money(Decimal("35"), "USD")),),
        requester_name="Dana",
    )
    await repository.add(request)
    gateway = FakeOrderGateway()
    use_case = SubmitPurchaseRequest(
        repository,
        SubmitOrder(gateway, ApprovalGatePolicy()),
    )

    with pytest.raises(DomainValidationError, match="approved decision"):
        await use_case.execute(request.id)

    assert gateway.submitted is False
    stored = await repository.get(request.id)
    assert stored is not None
    assert stored.status is RequestStatus.DRAFTING


async def test_submit_purchase_request_submits_approved_draft_and_marks_request_submitted(
    repository: PurchaseRequestRepository,
) -> None:
    item = PurchaseItem("Laptop stand", 1, Money(Decimal("35"), "USD"), "Trusted Vendor")
    request = PurchaseRequest.create((item,), requester_name="Dana")
    request.draft_order = CreateDraftOrder(DraftOrderPolicy()).execute(request, request.items)
    request.transition_to(RequestStatus.PENDING_APPROVAL)
    request.approval_decision = ApprovalDecision.create(
        request.id,
        ApprovalOutcome.APPROVED,
        "approver",
    )
    request.transition_to(RequestStatus.APPROVED)
    await repository.add(request)

    gateway = FakeOrderGateway()
    use_case = SubmitPurchaseRequest(
        repository,
        SubmitOrder(gateway, ApprovalGatePolicy()),
    )

    view = await use_case.execute(request.id)

    assert gateway.submitted is True
    assert view.status is RequestStatus.SUBMITTED
    stored = await repository.get(request.id)
    assert stored is not None
    assert stored.status is RequestStatus.SUBMITTED
    assert stored.audit_entries[-1].event_type == "order_submitted"
