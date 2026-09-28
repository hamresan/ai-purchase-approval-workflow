from decimal import Decimal

from ai_purchase_workflow.application.purchase_requests.trusted_tools import (
    BudgetReader,
    CatalogReader,
    OrderGateway,
    TrustedCatalogItem,
)
from ai_purchase_workflow.domain.purchase_requests import DomainValidationError, DraftOrder, Money


class FixtureBudgetReader(BudgetReader):
    def __init__(self) -> None:
        self._budgets = {"Dana": Money(Decimal("500.00"), "USD")}

    async def get_available_budget(self, requester_name: str | None, currency: str) -> Money:
        budget = self._budgets.get(requester_name or "")
        if budget is None or budget.currency != currency:
            raise DomainValidationError("No trusted budget data is available for this requester.")
        return budget


class FixtureCatalogReader(CatalogReader):
    def __init__(self) -> None:
        items = (
            TrustedCatalogItem(
                description="Laptop stand",
                vendor="Acme",
                unit_price=Money(Decimal("35.00"), "USD"),
                available_quantity=10,
            ),
            TrustedCatalogItem(
                description="Monitor",
                vendor="Northwind",
                unit_price=Money(Decimal("250.00"), "USD"),
                available_quantity=5,
            ),
        )
        self._items = {self._normalize_description(item.description): item for item in items}

    async def find_item(self, description: str) -> TrustedCatalogItem:
        item = self._items.get(self._normalize_description(description))
        if item is None:
            raise DomainValidationError(f"No trusted vendor data is available for {description}.")
        return item

    @staticmethod
    def _normalize_description(description: str) -> str:
        return " ".join(description.split()).casefold()


class FixtureOrderGateway(OrderGateway):
    async def submit(self, draft_order: DraftOrder) -> str:
        return f"fixture-order-{draft_order.id}"
