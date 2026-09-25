from decimal import Decimal

import pytest
from tests.application.purchase_requests.fakes.prompt import FakePromptTemplateReader
from tests.application.purchase_requests.fakes.repository import (
    InMemoryPurchaseRequestRepository,
)
from tests.application.purchase_requests.fakes.trusted_tools import (
    FakeBudgetReader,
    FakeCatalogReader,
)

from ai_purchase_workflow.application.purchase_requests.extraction import (
    ExtractedRequestValidator,
    ExtractPurchaseRequest,
    ModelResponse,
    PurchaseRequestPromptBuilder,
    StructuredOutputMapper,
)
from ai_purchase_workflow.application.purchase_requests.extraction.preparation import (
    PrepareExtractedPurchaseRequest,
)
from ai_purchase_workflow.application.purchase_requests.trusted_tools import (
    CheckBudget,
    CreateDraftOrder,
    FindVendor,
)
from ai_purchase_workflow.domain.purchase_requests import (
    BudgetPolicy,
    DraftOrderPolicy,
    RequestStatus,
    VendorPolicy,
)
from ai_purchase_workflow.infrastructure.models import FakePurchaseRequestModel
from ai_purchase_workflow.infrastructure.workflows import PurchaseRequestWorkflow


def build_workflow(
    content: object,
    *,
    catalog: FakeCatalogReader | None = None,
    budget: FakeBudgetReader | None = None,
) -> tuple[PurchaseRequestWorkflowRunner, InMemoryPurchaseRequestRepository]:
    repository = InMemoryPurchaseRequestRepository()
    extractor = ExtractPurchaseRequest(
        model=FakePurchaseRequestModel(ModelResponse(content)),
        prompt_builder=PurchaseRequestPromptBuilder(FakePromptTemplateReader()),
        mapper=StructuredOutputMapper(),
        validator=ExtractedRequestValidator(),
    )
    preparer = PrepareExtractedPurchaseRequest(
        repository=repository,
        find_vendor=FindVendor(catalog or FakeCatalogReader(), VendorPolicy()),
        create_draft_order=CreateDraftOrder(DraftOrderPolicy()),
        check_budget=CheckBudget(budget or FakeBudgetReader(), BudgetPolicy()),
    )
    workflow = PurchaseRequestWorkflow(
        ExtractPurchaseRequestNode(extractor),
        PreparePurchaseRequestNode(preparer),
    )
    return (
        PurchaseRequestWorkflowRunner(
            workflow,
            PurchaseRequestWorkflowStateFactory(),
            PurchaseRequestWorkflowResultMapper(),
        ),
        repository,
    )


@pytest.mark.asyncio
async def test_workflow_prepares_trusted_request_for_approval() -> None:
    workflow, repository = build_workflow(
        {
            "schema_version": "1.0",
            "requester_name": "Dana",
            "items": [{"description": "Laptop stand", "quantity": 2}],
        }
    )

    result = await workflow.execute("Dana needs two laptop stands", checkpoint_id="thread-1")

    assert result.checkpoint_id == "thread-1"
    assert result.status == "pending_approval"
    assert result.needs_human_review is False
    assert result.purchase_request_id is not None
    request = repository.requests[result.purchase_request_id]
    assert request.status is RequestStatus.PENDING_APPROVAL
    assert request.items[0].vendor == "Trusted Vendor"
    assert request.items[0].unit_price.amount == Decimal("25.00")
    assert request.draft_order is not None
    assert result.tool_results == (
        "trusted_data_resolved",
        "draft_order_created",
        "budget_checked",
    )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "content",
    [
        "malformed",
        {
            "schema_version": "1.0",
            "items": [],
            "needs_human_review": True,
            "review_reason": "Quantity is ambiguous.",
        },
        {
            "schema_version": "1.0",
            "items": [{"description": "Laptop stand", "quantity": 1}],
            "tool_calls": [{"name": "submit_order"}],
        },
    ],
)
async def test_workflow_routes_untrusted_model_results_to_human_review(content: object) -> None:
    workflow, repository = build_workflow(content)

    result = await workflow.execute("request")

    assert result.status == "human_review"
    assert result.needs_human_review is True
    assert result.purchase_request_id is None
    assert repository.requests == {}


@pytest.mark.asyncio
async def test_workflow_routes_tool_failure_to_human_review() -> None:
    workflow, repository = build_workflow(
        {
            "schema_version": "1.0",
            "requester_name": "Dana",
            "items": [{"description": "Unknown", "quantity": 1}],
        }
    )

    result = await workflow.execute("Dana needs an unknown item")

    assert result.status == "human_review"
    assert result.needs_human_review is True
    assert result.purchase_request_id is None
    assert "Trusted tool execution failed" in (result.review_reason or "")
    assert result.tool_results == ("prepare_failed",)
    assert len(repository.requests) == 0


@pytest.mark.asyncio
async def test_workflow_does_not_persist_request_when_budget_check_fails() -> None:
    workflow, repository = build_workflow(
        {
            "schema_version": "1.0",
            "requester_name": "Dana",
            "items": [{"description": "Laptop stand", "quantity": 2}],
        },
        budget=FakeBudgetReader("10.00"),
    )

    result = await workflow.execute("Dana needs two laptop stands")

    assert result.status == "human_review"
    assert result.needs_human_review is True
    assert result.purchase_request_id is None
    assert result.tool_results == ("prepare_failed",)
    assert repository.requests == {}
