from decimal import Decimal

import pytest

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


def item(quantity: int = 1, amount: str = "10.00", vendor: str | None = "Acme") -> PurchaseItem:
    return PurchaseItem("Laptop stand", quantity, Money(Decimal(amount), "USD"), vendor)


def test_budget_policy_rejects_over_budget() -> None:
    with pytest.raises(DomainValidationError, match="exceeds"):
        BudgetPolicy().ensure_within_budget(
            Money(Decimal("101"), "USD"),
            Money(Decimal("100"), "USD"),
        )


def test_vendor_policy_rejects_missing_vendor_and_unavailable_quantity() -> None:
    policy = VendorPolicy()
    with pytest.raises(DomainValidationError, match="trusted vendor"):
        policy.ensure_available(item(vendor=None), 10)
    with pytest.raises(DomainValidationError, match="unavailable"):
        policy.ensure_available(item(quantity=3), 2)


def test_draft_order_policy_calculates_total_and_rejects_mixed_currency() -> None:
    policy = DraftOrderPolicy()
    assert policy.calculate_total((item(quantity=2), item(amount="5.00"))).amount == Decimal(
        "25.00"
    )
    eur_item = PurchaseItem("Other", 1, Money(Decimal("1"), "EUR"), "Vendor")
    with pytest.raises(DomainValidationError, match="same currency"):
        policy.calculate_total((item(), eur_item))


def test_approval_gate_rejects_request_without_approved_decision() -> None:
    request = PurchaseRequest.create((item(),))
    with pytest.raises(DomainValidationError, match="approved decision"):
        ApprovalGatePolicy().ensure_submission_allowed(request)

    request.transition_to(RequestStatus.PENDING_APPROVAL)
    request.approval_decision = ApprovalDecision.create(
        request.id, ApprovalOutcome.REJECTED, "approver"
    )
    request.transition_to(RequestStatus.REJECTED)
    with pytest.raises(DomainValidationError, match="approved decision"):
        ApprovalGatePolicy().ensure_submission_allowed(request)
