from decimal import Decimal

from ai_purchase_workflow.domain.purchase_requests.entities import PurchaseItem, PurchaseRequest
from ai_purchase_workflow.domain.purchase_requests.enums import ApprovalOutcome, RequestStatus
from ai_purchase_workflow.domain.purchase_requests.errors import DomainValidationError
from ai_purchase_workflow.domain.purchase_requests.value_objects import Money


class BudgetPolicy:
    def ensure_within_budget(self, total: Money, available_budget: Money) -> None:
        if total.currency != available_budget.currency:
            raise DomainValidationError("Budget currency does not match the draft order currency.")
        if total.amount > available_budget.amount:
            raise DomainValidationError("Purchase request exceeds the available budget.")


class VendorPolicy:
    def ensure_available(self, item: PurchaseItem, available_quantity: int) -> None:
        if item.vendor is None:
            raise DomainValidationError("A trusted vendor is required.")
        if available_quantity < item.quantity:
            raise DomainValidationError(
                f"Requested quantity for {item.description} is unavailable."
            )


class DraftOrderPolicy:
    def calculate_total(self, items: tuple[PurchaseItem, ...]) -> Money:
        if not items:
            raise DomainValidationError("A draft order must contain at least one item.")
        currency = items[0].unit_price.currency
        if any(item.unit_price.currency != currency for item in items):
            raise DomainValidationError("All draft order items must use the same currency.")
        amount = sum((item.total_price.amount for item in items), start=Decimal("0"))
        return Money(amount, currency)


class ApprovalGatePolicy:
    def ensure_submission_allowed(self, request: PurchaseRequest) -> None:
        decision = request.approval_decision
        if (
            request.status is not RequestStatus.APPROVED
            or decision is None
            or decision.outcome is not ApprovalOutcome.APPROVED
        ):
            raise DomainValidationError("An approved decision is required before order submission.")
