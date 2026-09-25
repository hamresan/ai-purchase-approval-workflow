from decimal import Decimal

import pytest
from langgraph.checkpoint.memory import InMemorySaver
from tests.application.purchase_requests.fakes.prompt import FakePromptTemplateReader
from tests.application.purchase_requests.fakes.repository import (
    InMemoryPurchaseRequestRepository,
)
from tests.application.purchase_requests.fakes.trusted_tools import (
    FakeBudgetReader,
    FakeCatalogReader,
    FakeOrderGateway,
)
from tests.unit.infrastructure.workflows.fakes import InMemoryWorkflowThreadRepository

from ai_purchase_workflow.application.purchase_requests.extracted_preparation import (
    PrepareExtractedPurchaseRequest,
)
from ai_purchase_workflow.application.purchase_requests.extraction import (
    ExtractedRequestValidator,
    ExtractPurchaseRequest,
    ModelResponse,
    PurchaseRequestPromptBuilder,
    StructuredOutputMapper,
)
from ai_purchase_workflow.application.purchase_requests.preparation import (
    SubmitPurchaseRequest,
)
from ai_purchase_workflow.application.purchase_requests.trusted_tools import (
    CheckBudget,
    CreateDraftOrder,
    FindVendor,
    SubmitOrder,
)
from ai_purchase_workflow.domain.purchase_requests import (
    ApprovalGatePolicy,
    ApprovalDecision,
    ApprovalOutcome,
    BudgetPolicy,
    DraftOrderPolicy,
    RequestStatus,
    VendorPolicy,
)
from ai_purchase_workflow.infrastructure.models import FakePurchaseRequestModel
from ai_purchase_workflow.infrastructure.workflows import (
    AwaitApprovalNode,
    ExtractPurchaseRequestNode,
    PreparePurchaseRequestNode,
    PurchaseRequestWorkflow,
    PurchaseRequestWorkflowResultMapper,
    PurchaseRequestWorkflowRunner,
    PurchaseRequestWorkflowStateFactory,
    SubmitPurchaseRequestNode,
)


def build_workflow(
    content: object,
    *,
    catalog: FakeCatalogReader | None = None,
    budget: FakeBudgetReader | None = None,
) -> tuple[
    PurchaseRequestWorkflowRunner,
    PurchaseRequestWorkflow,
    InMemoryPurchaseRequestRepository,
    InMemoryWorkflowThreadRepository,
    FakeOrderGateway,
]:
    repository = InMemoryPurchaseRequestRepository()
    threads = InMemoryWorkflowThreadRepository()
    gateway = FakeOrderGateway()
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
    submitter = SubmitPurchaseRequest(
        repository,
        SubmitOrder(gateway, ApprovalGatePolicy()),
    )
    workflow = PurchaseRequestWorkflow(
        ExtractPurchaseRequestNode(extractor),
        PreparePurchaseRequestNode(preparer, threads),
        AwaitApprovalNode(),
        SubmitPurchaseRequestNode(submitter),
        InMemorySaver(),
    )
    return (
        PurchaseRequestWorkflowRunner(
            workflow,
            PurchaseRequestWorkflowStateFactory(),
            PurchaseRequestWorkflowResultMapper(),
        ),
        workflow,
        repository,
        threads,
        gateway,
    )


@pytest.mark.asyncio
async def test_workflow_pauses_before_submission_and_binds_thread() -> None:
    runner, _workflow, repository, threads, gateway = build_workflow(
        {
            "schema_version": "1.0",
            "requester_name": "Dana",
            "items": [{"description": "Laptop stand", "quantity": 2}],
        }
    )

    result = await runner.execute("Dana needs two laptop stands", checkpoint_id="thread-1")

    assert result.checkpoint_id == "thread-1"
    assert result.status == "pending_approval"
    assert result.purchase_request_id is not None
    request = repository.requests[result.purchase_request_id]
    assert request.status is RequestStatus.PENDING_APPROVAL
    assert request.items[0].vendor == "Trusted Vendor"
    assert request.items[0].unit_price.amount == Decimal("25.00")
    assert request.draft_order is not None
    assert await threads.get_thread_id(request.id) == "thread-1"
    assert gateway.submitted is False
    assert result.tool_results == (
        "trusted_data_resolved",
        "draft_order_created",
        "budget_checked",
        "approval_paused",
    )


@pytest.mark.asyncio
async def test_workflow_resumes_approved_request_and_submits_once() -> None:
    runner, workflow, repository, _threads, gateway = build_workflow(
        {
            "schema_version": "1.0",
            "requester_name": "Dana",
            "items": [{"description": "Laptop stand", "quantity": 1}],
        }
    )
    result = await runner.execute("Dana needs a laptop stand", checkpoint_id="thread-approved")
    assert result.purchase_request_id is not None
    request = repository.requests[result.purchase_request_id]
    request.approval_decision = ApprovalDecision.create(
        request.id,
        ApprovalOutcome.APPROVED,
        "manager",
    )
    request.transition_to(RequestStatus.APPROVED)
    await repository.save(request)

    resumed = await workflow.resume(thread_id="thread-approved", action="approved")

    assert resumed["status"] == "submitted"
    assert gateway.submitted is True
    assert repository.requests[request.id].status is RequestStatus.SUBMITTED


@pytest.mark.asyncio
async def test_workflow_resumes_rejected_request_without_submitting() -> None:
    runner, workflow, repository, _threads, gateway = build_workflow(
        {
            "schema_version": "1.0",
            "requester_name": "Dana",
            "items": [{"description": "Laptop stand", "quantity": 1}],
        }
    )
    result = await runner.execute("Dana needs a laptop stand", checkpoint_id="thread-rejected")
    assert result.purchase_request_id is not None
    request = repository.requests[result.purchase_request_id]
    request.approval_decision = ApprovalDecision.create(
        request.id,
        ApprovalOutcome.REJECTED,
        "manager",
    )
    request.transition_to(RequestStatus.REJECTED)
    await repository.save(request)

    resumed = await workflow.resume(thread_id="thread-rejected", action="rejected")

    assert resumed["status"] == "rejected"
    assert gateway.submitted is False


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
    runner, _workflow, repository, _threads, _gateway = build_workflow(content)

    result = await runner.execute("request")

    assert result.status == "human_review"
    assert result.needs_human_review is True
    assert result.purchase_request_id is None
    assert repository.requests == {}


@pytest.mark.asyncio
async def test_workflow_routes_tool_failure_to_human_review() -> None:
    runner, _workflow, repository, _threads, _gateway = build_workflow(
        {
            "schema_version": "1.0",
            "requester_name": "Dana",
            "items": [{"description": "Unknown", "quantity": 1}],
        }
    )

    result = await runner.execute("Dana needs an unknown item")

    assert result.status == "human_review"
    assert result.needs_human_review is True
    assert result.purchase_request_id is None
    assert "Trusted tool execution failed" in (result.review_reason or "")
    assert result.tool_results == ("prepare_failed",)
    assert repository.requests == {}


@pytest.mark.asyncio
async def test_workflow_does_not_persist_request_when_budget_check_fails() -> None:
    runner, _workflow, repository, _threads, _gateway = build_workflow(
        {
            "schema_version": "1.0",
            "requester_name": "Dana",
            "items": [{"description": "Laptop stand", "quantity": 2}],
        },
        budget=FakeBudgetReader("10.00"),
    )

    result = await runner.execute("Dana needs two laptop stands")

    assert result.status == "human_review"
    assert result.needs_human_review is True
    assert result.purchase_request_id is None
    assert result.tool_results == ("prepare_failed",)
    assert repository.requests == {}
