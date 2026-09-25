import pytest

from ai_purchase_workflow.application.purchase_requests.repository import (
    PurchaseRequestRepository,
)

from tests_support.purchase_requests import InMemoryPurchaseRequestRepository


@pytest.fixture
def repository() -> PurchaseRequestRepository:
    return InMemoryPurchaseRequestRepository()
