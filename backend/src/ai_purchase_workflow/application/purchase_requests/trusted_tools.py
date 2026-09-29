from typing import Protocol
from uuid import UUID

from ai_purchase_workflow.application.trusted_data import (
    BudgetConstraintReader,
    TrustedCatalogReader,
)
from ai_purchase_workflow.domain.purchase_requests import (
    DomainValidationError,
    DraftOrder,
    Money,
    PurchaseItem,
    PurchaseRequest,
)
from ai_purchase_workflow.domain.purchase_requests.policies import (
    ApprovalGatePolicy,
    BudgetPolicy,
    DraftOrderPolicy,
    VendorPolicy,
)


class OrderGateway(Protocol):
    async def submit(self, draft_order: DraftOrder) -> str: ...


class CheckBudget:
    def __init__(self, reader: BudgetConstraintReader, policy: BudgetPolicy) -> None:
        self._reader = reader
        self._policy = policy

    async def execute(self, requester_user_id: UUID | None, total: Money) -> None:
        if requester_user_id is None:
            raise DomainValidationError("An authenticated requester is required for budget checks.")
        constraints = await self._reader.get_applicable_constraints(
            requester_user_id,
            total.currency,
        )
        for constraint in constraints:
            self._policy.ensure_within_budget(total, constraint.available)


class FindVendor:
    def __init__(self, reader: TrustedCatalogReader, policy: VendorPolicy) -> None:
        self._reader = reader
        self._policy = policy

    async def execute(self, requested_item: PurchaseItem) -> PurchaseItem:
        return await self.resolve(requested_item.description, requested_item.quantity)

    async def resolve(self, description: str, quantity: int) -> PurchaseItem:
        trusted = await self._reader.find_item(description)
        resolved = PurchaseItem(
            description=trusted.description,
            quantity=quantity,
            unit_price=trusted.unit_price,
            vendor=trusted.vendor_name,
        )
        self._policy.ensure_available(resolved, trusted.available_quantity)
        return resolved


class CreateDraftOrder:
    def __init__(self, policy: DraftOrderPolicy) -> None:
        self._policy = policy

    def execute(self, request: PurchaseRequest, items: tuple[PurchaseItem, ...]) -> DraftOrder:
        return DraftOrder.create(
            request_id=request.id,
            items=items,
            total=self._policy.calculate_total(items),
        )


class SubmitOrder:
    def __init__(self, gateway: OrderGateway, policy: ApprovalGatePolicy) -> None:
        self._gateway = gateway
        self._policy = policy

    async def execute(self, request: PurchaseRequest) -> str:
        self._policy.ensure_submission_allowed(request)
        if request.draft_order is None:
            raise DomainValidationError("Approved purchase request has no draft order.")
        return await self._gateway.submit(request.draft_order)
