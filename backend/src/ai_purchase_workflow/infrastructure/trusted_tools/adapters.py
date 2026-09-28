from decimal import Decimal

from ai_purchase_workflow.application.purchase_requests.trusted_tools import (
    BudgetReader,
    CatalogReader,
    OrderGateway,
    TrustedCatalogItem,
)
from ai_purchase_workflow.domain.purchase_requests import DomainValidationError, DraftOrder, Money
from ai_purchase_workflow.infrastructure.trusted_tools.catalog_item_matcher import (
    CatalogItemMatcher,
)


class FixtureBudgetReader(BudgetReader):
    def __init__(self) -> None:
        self._budgets = {"Dana": Money(Decimal("500.00"), "USD")}

    async def get_available_budget(self, requester_name: str | None, currency: str) -> Money:
        budget = self._budgets.get(requester_name or "")
        if budget is None or budget.currency != currency:
            raise DomainValidationError("No trusted budget data is available for this requester.")
        return budget


class FixtureCatalogReader(CatalogReader):
    def __init__(self, matcher: CatalogItemMatcher | None = None) -> None:
        self._matcher = matcher or CatalogItemMatcher()
        self._items = (
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

    async def find_item(self, description: str) -> TrustedCatalogItem:
        item = next(
            (
                item
                for item in self._items
                if self._matcher.matches(description, item.description)
            ),
            None,
        )
        if item is None:
            raise DomainValidationError(f"No trusted vendor data is available for {description}.")
        return item


class FixtureOrderGateway(OrderGateway):
    async def submit(self, draft_order: DraftOrder) -> str:
        return f"fixture-order-{draft_order.id}"
