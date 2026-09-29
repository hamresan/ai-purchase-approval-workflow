from ai_purchase_workflow.application.purchase_requests import (
    CheckBudget,
    CreateDraftOrder,
    FindVendor,
    PurchaseRequestRepository,
    SubmitOrder,
)
from ai_purchase_workflow.application.purchase_requests.extracted_preparation import (
    PrepareExtractedPurchaseRequest,
)
from ai_purchase_workflow.application.purchase_requests.extraction import (
    ExtractedRequestValidator,
    ExtractPurchaseRequest,
    PurchaseRequestPromptBuilder,
    StructuredOutputMapper,
)
from ai_purchase_workflow.application.purchase_requests.preparation import SubmitPurchaseRequest
from ai_purchase_workflow.application.workflows import WorkflowThreadRepository
from ai_purchase_workflow.composition_root.models import build_purchase_request_model
from ai_purchase_workflow.composition_root.purchase_requests import build_submit_purchase_request
from ai_purchase_workflow.composition_root.settings import Settings
from ai_purchase_workflow.domain.purchase_requests import (
    ApprovalGatePolicy,
    BudgetPolicy,
    DraftOrderPolicy,
    VendorPolicy,
)
from ai_purchase_workflow.infrastructure.observability import LoggingWorkflowObserver
from ai_purchase_workflow.infrastructure.prompts import FilePromptTemplateReader
from sqlalchemy.ext.asyncio import AsyncSession

from ai_purchase_workflow.infrastructure.trusted_data.budget_reader import SqlAlchemyBudgetConstraintReader
from ai_purchase_workflow.infrastructure.trusted_data.catalog_reader import SqlAlchemyTrustedCatalogReader
from ai_purchase_workflow.infrastructure.trusted_tools import FixtureOrderGateway
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
)
from ai_purchase_workflow.infrastructure.workflows.checkpoint_types import CheckpointSaver
from ai_purchase_workflow.infrastructure.workflows.resume_only import (
    ResumeOnlyExtractNode,
    ResumeOnlyPrepareNode,
)


def build_start_purchase_request_workflow(
    repository: PurchaseRequestRepository,
    threads: WorkflowThreadRepository,
    checkpointer: CheckpointSaver,
    settings: Settings,
    session: AsyncSession,
) -> PurchaseRequestWorkflowRunner:
    observer = LoggingWorkflowObserver()
    extractor = ExtractPurchaseRequest(
        model=build_purchase_request_model(settings),
        prompt_builder=PurchaseRequestPromptBuilder(FilePromptTemplateReader()),
        mapper=StructuredOutputMapper(),
        validator=ExtractedRequestValidator(),
    )
    preparer = PrepareExtractedPurchaseRequest(
        repository=repository,
        find_vendor=FindVendor(SqlAlchemyTrustedCatalogReader(session), VendorPolicy()),
        create_draft_order=CreateDraftOrder(DraftOrderPolicy()),
        check_budget=CheckBudget(SqlAlchemyBudgetConstraintReader(session), BudgetPolicy()),
    )
    submitter = SubmitPurchaseRequest(
        repository,
        SubmitOrder(FixtureOrderGateway(), ApprovalGatePolicy()),
    )
    workflow = PurchaseRequestWorkflow(
        ExtractPurchaseRequestNode(extractor),
        PreparePurchaseRequestNode(preparer, threads, observer),
        AwaitApprovalNode(),
        SubmitPurchaseRequestNode(submitter, observer),
        checkpointer,
    )
    return PurchaseRequestWorkflowRunner(
        workflow,
        PurchaseRequestWorkflowStateFactory(),
        PurchaseRequestWorkflowResultMapper(),
        observer,
    )


def build_resume_purchase_request_workflow(
    repository: PurchaseRequestRepository,
    checkpointer: CheckpointSaver,
) -> PurchaseRequestWorkflow:
    observer = LoggingWorkflowObserver()
    return PurchaseRequestWorkflow(
        extract_node=ResumeOnlyExtractNode(),
        prepare_node=ResumeOnlyPrepareNode(),
        await_approval_node=AwaitApprovalNode(),
        submit_node=SubmitPurchaseRequestNode(
            build_submit_purchase_request(repository),
            observer,
        ),
        checkpointer=checkpointer,
    )


def build_workflow_gateway(
    repository: PurchaseRequestRepository,
    threads: WorkflowThreadRepository,
    checkpointer: CheckpointSaver,
) -> LangGraphPurchaseRequestWorkflowGateway:
    workflow = build_resume_purchase_request_workflow(repository, checkpointer)
    return LangGraphPurchaseRequestWorkflowGateway(workflow, threads)
