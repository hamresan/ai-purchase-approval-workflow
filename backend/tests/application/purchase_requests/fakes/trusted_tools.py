from decimal import Decimal

from ai_purchase_workflow.application.purchase_requests.trusted_tools import (
    BudgetReader,
    CatalogReader,
    OrderGateway,
    TrustedCatalogItem,
)
from ai_purchase_workflow.domain.purchase_requests import DomainValidationError, DraftOrder, Money


class FakeBudgetReader(BudgetReader):
    def __init__(self, amount: str = "500.00") -> None:
        self._amount = Decimal(amount)

    async def get_available_budget(self, requester_name: str | None, currency: str) -> Money:
        if requester_name is None:
            raise DomainValidationError("No trusted budget data is available for this requester.")
        return Money(self._amount, currency)


class FakeCatalogReader(CatalogReader):
    def __init__(self, available_quantity: int = 10) -> None:
        self._available_quantity = available_quantity

    async def find_item(self, description: str) -> TrustedCatalogItem:
        if description == "Unknown":
            raise DomainValidationError("No trusted vendor data is available for Unknown.")
        return TrustedCatalogItem(
            description=description,
            vendor="Trusted Vendor",
            unit_price=Money(Decimal("25.00"), "USD"),
            available_quantity=self._available_quantity,
        )


class FakeOrderGateway(OrderGateway):
    def __init__(self) -> None:
        self.submitted = False

    async def submit(self, draft_order: DraftOrder) -> str:
        self.submitted = True
        return f"order-{draft_order.id}"
