import asyncio
import os
from uuid import uuid4

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from ai_purchase_workflow.application.purchase_requests.extracted_preparation import PrepareExtractedPurchaseRequest
from ai_purchase_workflow.application.purchase_requests.extraction import ExtractedRequestValidator, ExtractPurchaseRequest, ModelResponse, PurchaseRequestPromptBuilder, StructuredOutputMapper
from ai_purchase_workflow.application.purchase_requests.preparation import SubmitPurchaseRequest
from ai_purchase_workflow.application.purchase_requests.trusted_tools import CheckBudget, CreateDraftOrder, FindVendor, SubmitOrder
from ai_purchase_workflow.domain.purchase_requests import ApprovalGatePolicy, BudgetPolicy, DraftOrderPolicy, VendorPolicy
from ai_purchase_workflow.infrastructure.models import FakePurchaseRequestModel
from ai_purchase_workflow.infrastructure.observability import LoggingWorkflowObserver
from ai_purchase_workflow.infrastructure.persistence.purchase_requests import SqlAlchemyPurchaseRequestRepository
from ai_purchase_workflow.infrastructure.persistence.workflow_threads import SqlAlchemyWorkflowThreadRepository
from ai_purchase_workflow.infrastructure.prompts import FilePromptTemplateReader
from ai_purchase_workflow.infrastructure.trusted_tools import FixtureBudgetReader, FixtureCatalogReader, FixtureOrderGateway
from ai_purchase_workflow.infrastructure.workflows import AwaitApprovalNode, ExtractPurchaseRequestNode, PreparePurchaseRequestNode, PurchaseRequestWorkflow, PurchaseRequestWorkflowResultMapper, PurchaseRequestWorkflowRunner, PurchaseRequestWorkflowStateFactory, SubmitPurchaseRequestNode, postgres_checkpointer


async def seed() -> None:
    database_url = os.environ["TEST_DATABASE_URL"]
    engine = create_async_engine(database_url)
    factory = async_sessionmaker(engine, expire_on_commit=False)
    observer = LoggingWorkflowObserver()
    try:
        async with factory() as session:
            repository = SqlAlchemyPurchaseRequestRepository(session)
            threads = SqlAlchemyWorkflowThreadRepository(session)
            extractor = ExtractPurchaseRequest(
                FakePurchaseRequestModel(ModelResponse({"schema_version": "1.0", "requester_name": "Dana", "items": [{"description": "Laptop stand", "quantity": 1}]})),
                PurchaseRequestPromptBuilder(FilePromptTemplateReader()),
                StructuredOutputMapper(),
                ExtractedRequestValidator(),
            )
            preparer = PrepareExtractedPurchaseRequest(repository, FindVendor(FixtureCatalogReader(), VendorPolicy()), CreateDraftOrder(DraftOrderPolicy()), CheckBudget(FixtureBudgetReader(), BudgetPolicy()))
            submitter = SubmitPurchaseRequest(repository, SubmitOrder(FixtureOrderGateway(), ApprovalGatePolicy()))
            async with postgres_checkpointer(database_url) as checkpointer:
                workflow = PurchaseRequestWorkflow(ExtractPurchaseRequestNode(extractor), PreparePurchaseRequestNode(preparer, threads, observer), AwaitApprovalNode(), SubmitPurchaseRequestNode(submitter, observer), checkpointer)
                runner = PurchaseRequestWorkflowRunner(workflow, PurchaseRequestWorkflowStateFactory(), PurchaseRequestWorkflowResultMapper(), observer)
                result = await runner.execute("Dana needs a laptop stand", checkpoint_id=f"e2e-{uuid4()}")
            if result.status != "pending_approval" or result.purchase_request_id is None:
                raise RuntimeError(f"E2E seed did not reach approval: {result.status}")
            print(result.purchase_request_id)
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed())
