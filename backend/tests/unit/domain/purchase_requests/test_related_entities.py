from dataclasses import FrozenInstanceError
from decimal import Decimal

import pytest

from ai_purchase_workflow.domain.purchase_requests import (
    ApprovalDecision,
    ApprovalOutcome,
    DomainValidationError,
    DraftOrder,
    Money,
    PurchaseItem,
    PurchaseRequest,
)


def make_request() -> PurchaseRequest:
    item = PurchaseItem("Dock", 1, Money(Decimal("120.00"), "USD"), "Acme")
    return PurchaseRequest.create(items=(item,), requester_name="Taylor")


def test_draft_order_requires_items() -> None:
    request = make_request()

    with pytest.raises(DomainValidationError, match="at least one item"):
        DraftOrder.create(request.id, (), Money(Decimal("0"), "USD"))


def test_approval_decision_requires_actor_and_has_immutable_meaning() -> None:
    request = make_request()
    decision = ApprovalDecision.create(
        request.id,
        ApprovalOutcome.APPROVED,
        "Manager",
        "Within policy",
    )

    assert decision.outcome is ApprovalOutcome.APPROVED
    assert decision.reason == "Within policy"
    with pytest.raises(FrozenInstanceError):
        decision.reason = "Changed"  # type: ignore[misc]


def test_approval_decision_rejects_blank_actor() -> None:
    request = make_request()

    with pytest.raises(DomainValidationError, match="Decided by"):
        ApprovalDecision.create(request.id, ApprovalOutcome.REJECTED, " ")
