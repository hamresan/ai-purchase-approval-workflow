from decimal import Decimal
from uuid import UUID, uuid4

import pytest
from tests.application.purchase_requests.fakes.idempotency import (
    InMemoryIdempotentPurchaseRequestCreator,
)
from tests.application.purchase_requests.fakes.repository import (
    InMemoryPurchaseRequestRepository,
)
from tests.application.purchase_requests.fakes.workflow_starter import (
    FakePurchaseRequestWorkflowStarter,
)

from ai_purchase_workflow.application.purchase_requests import (
    CreatePurchaseItem,
    CreatePurchaseRequest,
    CreatePurchaseRequestCommand,
    GetPurchaseRequest,
    PurchaseRequestWorkflowReviewRequiredError,
    PurchaseRequestWorkflowStartResult,
    SubmitFreeTextPurchaseRequest,
    SubmitFreeTextPurchaseRequestCommand,
)


@pytest.mark.asyncio
async def test_submit_free_text_builds_context_and_returns_persisted_request() -> None:
    repository = InMemoryPurchaseRequestRepository()
    created = await CreatePurchaseRequest(
        repository,
        InMemoryIdempotentPurchaseRequestCreator(),
    ).execute(
        CreatePurchaseRequestCommand(
            requester_name="Dana",
            items=(CreatePurchaseItem("Laptop stand", 1, Decimal("35"), "USD", "Acme"),),
        )
    )
    workflow = FakePurchaseRequestWorkflowStarter(
        PurchaseRequestWorkflowStartResult(purchase_request_id=created.id)
    )
    use_case = SubmitFreeTextPurchaseRequest(workflow, GetPurchaseRequest(repository))

    result = await use_case.execute(
        SubmitFreeTextPurchaseRequestCommand(
            request_text="I need one laptop stand",
            requester_name="Dana",
            requester_user_id=UUID("11111111-1111-1111-1111-111111111111"),
        )
    )

    assert result.id == created.id
    assert workflow.free_texts == ["Requester: Dana\nRequest: I need one laptop stand"]


@pytest.mark.asyncio
async def test_submit_free_text_raises_safe_review_error_when_workflow_cannot_create() -> None:
    repository = InMemoryPurchaseRequestRepository()
    workflow = FakePurchaseRequestWorkflowStarter(
        PurchaseRequestWorkflowStartResult(
            purchase_request_id=None,
            review_reason="The request needs clarification.",
        )
    )
    use_case = SubmitFreeTextPurchaseRequest(workflow, GetPurchaseRequest(repository))

    with pytest.raises(
        PurchaseRequestWorkflowReviewRequiredError,
        match="needs clarification",
    ):
        await use_case.execute(
            SubmitFreeTextPurchaseRequestCommand(request_text="Please purchase equipment")
        )


@pytest.mark.asyncio
async def test_submit_free_text_uses_fallback_review_message() -> None:
    repository = InMemoryPurchaseRequestRepository()
    workflow = FakePurchaseRequestWorkflowStarter(
        PurchaseRequestWorkflowStartResult(purchase_request_id=None)
    )
    use_case = SubmitFreeTextPurchaseRequest(workflow, GetPurchaseRequest(repository))

    with pytest.raises(
        PurchaseRequestWorkflowReviewRequiredError,
        match="needs more information",
    ):
        await use_case.execute(
            SubmitFreeTextPurchaseRequestCommand(request_text=f"request-{uuid4()}")
        )
