from decimal import Decimal
from uuid import UUID, uuid4

from ai_purchase_workflow.application.purchase_requests.trusted_tools import OrderGateway
from ai_purchase_workflow.application.trusted_data import (
    BudgetConstraint,
    BudgetConstraintReader,
    TrustedCatalogItem,
    TrustedCatalogReader,
)
from ai_purchase_workflow.domain.purchase_requests import DomainValidationError, DraftOrder, Money


class FakeBudgetReader(BudgetConstraintReader):
    def __init__(self, *amounts: str) -> None:
        self._amounts = amounts or ("500.00",)
        self.requester_user_ids: list[UUID] = []

    async def get_applicable_constraints(
        self,
        requester_user_id: UUID,
        currency: str,
    ) -> tuple[BudgetConstraint, ...]:
        self.requester_user_ids.append(requester_user_id)
        return tuple(
            BudgetConstraint(
                owner_type="USER" if index == 0 else "DEPARTMENT",
                owner_id=requester_user_id,
                available=Money(Decimal(amount), currency),
            )
            for index, amount in enumerate(self._amounts)
        )


class FakeCatalogReader(TrustedCatalogReader):
    def __init__(self, available_quantity: int = 10) -> None:
        self._available_quantity = available_quantity

    async def find_item(self, description: str) -> TrustedCatalogItem:
        if description == "Unknown":
            raise DomainValidationError("No trusted vendor data is available for Unknown.")
        return TrustedCatalogItem(
            product_id=uuid4(),
            description=description,
            vendor_id=uuid4(),
            vendor_name="Trusted Vendor",
            unit_price=Money(Decimal("25.00"), "USD"),
            available_quantity=self._available_quantity,
        )


class FakeOrderGateway(OrderGateway):
    def __init__(self) -> None:
        self.submitted = False

    async def submit(self, draft_order: DraftOrder) -> str:
        self.submitted = True
        return f"order-{draft_order.id}"
