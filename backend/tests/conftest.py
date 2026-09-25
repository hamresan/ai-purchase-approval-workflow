import pytest

from ai_purchase_workflow.application.purchase_requests.repository import PurchaseRequestRepository
from tests.application.purchase_requests.fakes import InMemoryPurchaseRequestRepository


@pytest.fixture
def repository() -> PurchaseRequestRepository:
    return InMemoryPurchaseRequestRepository()
