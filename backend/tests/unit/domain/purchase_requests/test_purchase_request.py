from dataclasses import FrozenInstanceError
from decimal import Decimal

import pytest

from ai_purchase_workflow.domain.purchase_requests import (
    AuditEntry,
    DomainValidationError,
    InvalidRequestTransitionError,
    Money,
    PurchaseItem,
    PurchaseRequest,
    RequestStatus,
)


def make_item() -> PurchaseItem:
    return PurchaseItem("Laptop stand", 2, Money(Decimal("35.00"), "USD"), "Acme")


def test_purchase_request_requires_at_least_one_item() -> None:
    with pytest.raises(DomainValidationError, match="at least one item"):
        PurchaseRequest.create(items=())


def test_purchase_item_rejects_missing_description_and_invalid_quantity() -> None:
    with pytest.raises(DomainValidationError, match="description"):
        PurchaseItem(" ", 1, Money(Decimal("1"), "USD"))
    with pytest.raises(DomainValidationError, match="quantity"):
        PurchaseItem("Cable", 0, Money(Decimal("1"), "USD"))


def test_purchase_request_allows_only_explicit_lifecycle_transitions() -> None:
    request = PurchaseRequest.create(items=(make_item(),))

    request.transition_to(RequestStatus.PENDING_APPROVAL)
    request.transition_to(RequestStatus.APPROVED)
    request.transition_to(RequestStatus.SUBMITTED)

    assert request.status is RequestStatus.SUBMITTED


@pytest.mark.parametrize(
    ("start", "target"),
    [
        (RequestStatus.DRAFTING, RequestStatus.APPROVED),
        (RequestStatus.PENDING_APPROVAL, RequestStatus.SUBMITTED),
        (RequestStatus.REJECTED, RequestStatus.APPROVED),
        (RequestStatus.SUBMITTED, RequestStatus.FAILED),
        (RequestStatus.FAILED, RequestStatus.DRAFTING),
    ],
)
def test_purchase_request_rejects_forbidden_transitions(
    start: RequestStatus, target: RequestStatus
) -> None:
    request = PurchaseRequest.create(items=(make_item(),))
    if start is RequestStatus.PENDING_APPROVAL:
        request.transition_to(RequestStatus.PENDING_APPROVAL)
    elif start is RequestStatus.REJECTED:
        request.transition_to(RequestStatus.PENDING_APPROVAL)
        request.transition_to(RequestStatus.REJECTED)
    elif start is RequestStatus.SUBMITTED:
        request.transition_to(RequestStatus.PENDING_APPROVAL)
        request.transition_to(RequestStatus.APPROVED)
        request.transition_to(RequestStatus.SUBMITTED)
    elif start is RequestStatus.FAILED:
        request.transition_to(RequestStatus.FAILED)

    with pytest.raises(InvalidRequestTransitionError):
        request.transition_to(target)


def test_audit_entry_is_immutable_and_has_stable_meaning() -> None:
    request = PurchaseRequest.create(items=(make_item(),))
    entry = AuditEntry.create(request.id, "request_created", "Purchase request created.")

    assert entry.event_type == "request_created"
    assert entry.message == "Purchase request created."
    with pytest.raises(FrozenInstanceError):
        entry.message = "Changed"  # type: ignore[misc]
