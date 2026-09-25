from dataclasses import dataclass
from decimal import Decimal, InvalidOperation

from ai_purchase_workflow.domain.purchase_requests.errors import DomainValidationError


@dataclass(frozen=True, slots=True)
class Money:
    amount: Decimal
    currency: str

    def __post_init__(self) -> None:
        try:
            normalized_amount = Decimal(self.amount)
        except (InvalidOperation, ValueError) as exc:
            raise DomainValidationError("Money amount must be a valid decimal.") from exc
        if not normalized_amount.is_finite():
            raise DomainValidationError("Money amount must be finite.")
        if normalized_amount < 0:
            raise DomainValidationError("Money amount cannot be negative.")
        normalized_currency = self.currency.strip().upper()
        if len(normalized_currency) != 3 or not normalized_currency.isalpha():
            raise DomainValidationError("Currency must be a three-letter alphabetic code.")
        object.__setattr__(self, "amount", normalized_amount)
        object.__setattr__(self, "currency", normalized_currency)

    def multiply(self, quantity: int) -> "Money":
        if quantity <= 0:
            raise DomainValidationError("Quantity must be greater than zero.")
        return Money(self.amount * quantity, self.currency)
