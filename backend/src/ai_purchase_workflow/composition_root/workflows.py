from ai_purchase_workflow.application.purchase_requests import PurchaseRequestRepository
from ai_purchase_workflow.application.workflows import WorkflowThreadRepository
from ai_purchase_workflow.composition_root.purchase_requests import (
    build_submit_purchase_request,
)
from ai_purchase_workflow.infrastructure.workflows import (
    AwaitApprovalNode,
    LangGraphPurchaseRequestWorkflowGateway,
    PurchaseRequestWorkflow,
    SubmitPurchaseRequestNode,
)
from ai_purchase_workflow.infrastructure.workflows.checkpoint_types import CheckpointSaver
from ai_purchase_workflow.infrastructure.workflows.resume_only import (
    ResumeOnlyExtractNode,
    ResumeOnlyPrepareNode,
)


def build_resume_purchase_request_workflow(
    repository: PurchaseRequestRepository,
    checkpointer: CheckpointSaver,
) -> PurchaseRequestWorkflow:
    return PurchaseRequestWorkflow(
        extract_node=ResumeOnlyExtractNode(),
        prepare_node=ResumeOnlyPrepareNode(),
        await_approval_node=AwaitApprovalNode(),
        submit_node=SubmitPurchaseRequestNode(build_submit_purchase_request(repository)),
        checkpointer=checkpointer,
    )


def build_workflow_gateway(
    repository: PurchaseRequestRepository,
    threads: WorkflowThreadRepository,
    checkpointer: CheckpointSaver,
) -> LangGraphPurchaseRequestWorkflowGateway:
    workflow = build_resume_purchase_request_workflow(repository, checkpointer)
    return LangGraphPurchaseRequestWorkflowGateway(workflow, threads)
