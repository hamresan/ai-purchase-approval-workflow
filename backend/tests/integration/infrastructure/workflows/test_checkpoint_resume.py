from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from tests.application.purchase_requests.fakes.prompt import FakePromptTemplateReader
from tests.application.purchase_requests.fakes.trusted_tools import (
    FakeBudgetReader,
    FakeCatalogReader,
    FakeOrderGateway,
)

from ai_purchase_workflow.application.purchase_requests.approval import ApprovePurchaseRequest
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
from ai_purchase_workflow.application.purchase_requests.preparation import SubmitPurchaseRequest
from ai_purchase_workflow.application.purchase_requests.trusted_tools import (
    CheckBudget,
    CreateDraftOrder,
    FindVendor,
    SubmitOrder,
)
from ai_purchase_workflow.domain.purchase_requests import (
    ApprovalGatePolicy,
    BudgetPolicy,
    DraftOrderPolicy,
    RequestStatus,
    VendorPolicy,
)
from ai_purchase_workflow.infrastructure.models import FakePurchaseRequestModel
from ai_purchase_workflow.infrastructure.persistence.purchase_requests import (
    SqlAlchemyPurchaseRequestRepository,
)
from ai_purchase_workflow.infrastructure.persistence.workflow_threads import (
    SqlAlchemyWorkflowThreadRepository,
)
from ai_purchase_workflow.infrastructure.workflows import (
    AwaitApprovalNode,
    ExtractPurchaseRequestNode,
    LangGraphPurchaseRequestWorkflowGateway,
    PreparePurchaseRequestNode,
    PurchaseRequestWorkflow,
    PurchaseRequestWorkflowResultMapper,
    PurchaseRequestWorkflowRunner,
    PurchaseRequestWorkflowStateFactory,
    SubmitPurchaseRequestNode,
    postgres_checkpointer,
)
from ai_purchase_workflow.infrastructure.workflows.resume_only import (
    ResumeOnlyExtractNode,
    ResumeOnlyPrepareNode,
)


async def test_postgres_checkpoint_survives_connection_and_resumes_approved_request(
    session_factory: async_sessionmaker[AsyncSession],
    test_database_url: str,
) -> None:
    thread_id = "integration-persisted-approval"
    order_gateway = FakeOrderGateway()

    async with session_factory() as session:
        repository = SqlAlchemyPurchaseRequestRepository(session)
        threads = SqlAlchemyWorkflowThreadRepository(session)
        extractor = ExtractPurchaseRequest(
            model=FakePurchaseRequestModel(
                ModelResponse(
                    {
                        "schema_version": "1.0",
                        "requester_name": "Dana",
                        "items": [{"description": "Laptop stand", "quantity": 1}],
                    }
                )
            ),
            prompt_builder=PurchaseRequestPromptBuilder(FakePromptTemplateReader()),
            mapper=StructuredOutputMapper(),
            validator=ExtractedRequestValidator(),
        )
        preparer = PrepareExtractedPurchaseRequest(
            repository=repository,
            find_vendor=FindVendor(FakeCatalogReader(), VendorPolicy()),
            create_draft_order=CreateDraftOrder(DraftOrderPolicy()),
            check_budget=CheckBudget(FakeBudgetReader(), BudgetPolicy()),
        )
        submitter = SubmitPurchaseRequest(
            repository,
            SubmitOrder(order_gateway, ApprovalGatePolicy()),
        )

        async with postgres_checkpointer(test_database_url) as checkpointer:
            workflow = PurchaseRequestWorkflow(
                ExtractPurchaseRequestNode(extractor),
                PreparePurchaseRequestNode(preparer, threads),
                AwaitApprovalNode(),
                SubmitPurchaseRequestNode(submitter),
                checkpointer,
            )
            runner = PurchaseRequestWorkflowRunner(
                workflow,
                PurchaseRequestWorkflowStateFactory(),
                PurchaseRequestWorkflowResultMapper(),
            )
            paused = await runner.execute(
                "Dana needs a laptop stand",
                checkpoint_id=thread_id,
            )

        assert paused.status == "pending_approval"
        assert paused.purchase_request_id is not None
        request_id = paused.purchase_request_id
        assert await threads.get_thread_id(request_id) == thread_id

    async with session_factory() as resumed_session:
        repository = SqlAlchemyPurchaseRequestRepository(resumed_session)
        threads = SqlAlchemyWorkflowThreadRepository(resumed_session)
        submitter = SubmitPurchaseRequest(
            repository,
            SubmitOrder(order_gateway, ApprovalGatePolicy()),
        )

        async with postgres_checkpointer(test_database_url) as checkpointer:
            workflow = PurchaseRequestWorkflow(
                ResumeOnlyExtractNode(),
                ResumeOnlyPrepareNode(),
                AwaitApprovalNode(),
                SubmitPurchaseRequestNode(submitter),
                checkpointer,
            )
            approval = ApprovePurchaseRequest(
                repository,
                LangGraphPurchaseRequestWorkflowGateway(workflow, threads),
            )
            approved = await approval.execute(request_id, decided_by="manager")

        assert approved.status is RequestStatus.SUBMITTED
        assert order_gateway.submitted is True

        persisted = await repository.get(request_id)
        assert persisted is not None
        assert persisted.status is RequestStatus.SUBMITTED
        assert persisted.approval_decision is not None
        assert [entry.event_type for entry in persisted.audit_entries] == [
            "request_extracted",
            "trusted_data_validated",
            "approval_paused",
            "approval_approved",
            "order_submitted",
        ]
