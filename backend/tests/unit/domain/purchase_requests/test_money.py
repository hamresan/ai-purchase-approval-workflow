from decimal import Decimal

import pytest

from ai_purchase_workflow.domain.purchase_requests import DomainValidationError, Money


def test_money_normalizes_currency_and_preserves_decimal_amount() -> None:
    money = Money(Decimal("12.50"), " usd ")

    assert money.amount == Decimal("12.50")
    assert money.currency == "USD"


@pytest.mark.parametrize("amount", [Decimal("-0.01"), Decimal("NaN"), Decimal("Infinity")])
def test_money_rejects_invalid_amount(amount: Decimal) -> None:
    with pytest.raises(DomainValidationError):
        Money(amount, "USD")


@pytest.mark.parametrize("currency", ["", "US", "US1", "USDD"])
def test_money_rejects_invalid_currency(currency: str) -> None:
    with pytest.raises(DomainValidationError):
        Money(Decimal("1.00"), currency)
