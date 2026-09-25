from dataclasses import dataclass
from decimal import Decimal

from ai_purchase_workflow.domain.purchase_requests.errors import DomainValidationError


@dataclass(frozen=True, slots=True)
class RequiredText:
    value: str
    field_name: str

    def __post_init__(self) -> None:
        normalized = self.value.strip()
        if not normalized:
            raise DomainValidationError(f"{self.field_name} is required.")
        object.__setattr__(self, "value", normalized)


@dataclass(frozen=True, slots=True)
class Money:
    amount: Decimal
    currency: str

    def __post_init__(self) -> None:
        if not self.amount.is_finite():
            raise DomainValidationError("Money amount must be finite.")
        if self.amount < 0:
            raise DomainValidationError("Money amount cannot be negative.")
        normalized_currency = self.currency.strip().upper()
        if len(normalized_currency) != 3 or not normalized_currency.isalpha():
            raise DomainValidationError("Currency must be a three-letter alphabetic code.")
        object.__setattr__(self, "currency", normalized_currency)

    def multiply(self, quantity: int) -> "Money":
        if quantity <= 0:
            raise DomainValidationError("Quantity must be greater than zero.")
        return Money(self.amount * quantity, self.currency)
