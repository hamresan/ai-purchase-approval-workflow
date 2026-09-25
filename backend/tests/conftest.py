import pytest
from tests.application.purchase_requests.fakes import InMemoryPurchaseRequestRepository

from ai_purchase_workflow.application.purchase_requests.repository import PurchaseRequestRepository


@pytest.fixture
def repository() -> PurchaseRequestRepository:
    return InMemoryPurchaseRequestRepository()
