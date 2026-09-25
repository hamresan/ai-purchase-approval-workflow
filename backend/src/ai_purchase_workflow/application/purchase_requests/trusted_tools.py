from dataclasses import dataclass
from typing import Protocol

from ai_purchase_workflow.domain.purchase_requests import DraftOrder, Money, PurchaseItem, PurchaseRequest
from ai_purchase_workflow.domain.purchase_requests.policies import (
    ApprovalGatePolicy,
    BudgetPolicy,
    DraftOrderPolicy,
    VendorPolicy,
)


@dataclass(frozen=True, slots=True)
class TrustedCatalogItem:
    description: str
    vendor: str
    unit_price: Money
    available_quantity: int


class BudgetReader(Protocol):
    async def get_available_budget(self, requester_name: str | None, currency: str) -> Money: ...


class CatalogReader(Protocol):
    async def find_item(self, description: str) -> TrustedCatalogItem: ...


class OrderGateway(Protocol):
    async def submit(self, draft_order: DraftOrder) -> str: ...


class CheckBudget:
    def __init__(self, reader: BudgetReader, policy: BudgetPolicy) -> None:
        self._reader = reader
        self._policy = policy

    async def execute(self, requester_name: str | None, total: Money) -> None:
        budget = await self._reader.get_available_budget(requester_name, total.currency)
        self._policy.ensure_within_budget(total, budget)


class FindVendor:
    def __init__(self, reader: CatalogReader, policy: VendorPolicy) -> None:
        self._reader = reader
        self._policy = policy

    async def execute(self, requested_item: PurchaseItem) -> PurchaseItem:
        trusted = await self._reader.find_item(requested_item.description)
        resolved = PurchaseItem(
            description=trusted.description,
            quantity=requested_item.quantity,
            unit_price=trusted.unit_price,
            vendor=trusted.vendor,
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
            raise ValueError("Approved purchase request has no draft order.")
        return await self._gateway.submit(request.draft_order)
