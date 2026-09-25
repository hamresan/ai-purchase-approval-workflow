from decimal import Decimal

import pytest

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


def requested_item(quantity: int = 1) -> PurchaseItem:
    return PurchaseItem(
        "Laptop stand",
        quantity,
        Money(Decimal("999.00"), "USD"),
        "Untrusted Vendor",
    )


async def test_find_vendor_uses_trusted_source_of_truth() -> None:
    resolved = await FindVendor(FakeCatalogReader(), VendorPolicy()).execute(requested_item())
    assert resolved.vendor == "Trusted Vendor"
    assert resolved.unit_price.amount == Decimal("25.00")


async def test_find_vendor_rejects_unavailable_quantity() -> None:
    with pytest.raises(DomainValidationError, match="unavailable"):
        await FindVendor(FakeCatalogReader(available_quantity=1), VendorPolicy()).execute(
            requested_item(quantity=2)
        )


async def test_check_budget_rejects_over_budget() -> None:
    tool = CheckBudget(FakeBudgetReader("20.00"), BudgetPolicy())
    with pytest.raises(DomainValidationError, match="exceeds"):
        await tool.execute("Dana", Money(Decimal("25.00"), "USD"))


async def test_submit_order_requires_approval_before_gateway_call() -> None:
    gateway = FakeOrderGateway()
    tool = SubmitOrder(gateway, ApprovalGatePolicy())
    request = PurchaseRequest.create((requested_item(),))
    request.draft_order = CreateDraftOrder(DraftOrderPolicy()).execute(request, request.items)

    with pytest.raises(DomainValidationError, match="approved decision"):
        await tool.execute(request)
    assert gateway.submitted is False

    request.transition_to(RequestStatus.PENDING_APPROVAL)
    request.approval_decision = ApprovalDecision.create(
        request.id, ApprovalOutcome.APPROVED, "approver"
    )
    request.transition_to(RequestStatus.APPROVED)
    await tool.execute(request)
    assert gateway.submitted is True
