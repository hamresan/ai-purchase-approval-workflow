from sqlalchemy.ext.asyncio import AsyncSession

from ai_purchase_workflow.application.purchase_requests import (
    ApprovePurchaseRequest,
    CheckBudget,
    CreateDraftOrder,
    EditPurchaseRequest,
    FindVendor,
    PreparePurchaseRequest,
    PurchaseRequestRepository,
    PurchaseRequestWorkflowGateway,
    RejectPurchaseRequest,
    SubmitOrder,
    SubmitPurchaseRequest,
)
from ai_purchase_workflow.domain.purchase_requests import (
    ApprovalGatePolicy,
    BudgetPolicy,
    DraftOrderPolicy,
    VendorPolicy,
)
from ai_purchase_workflow.infrastructure.trusted_data.budget_reader import (
    SqlAlchemyBudgetConstraintReader,
)
from ai_purchase_workflow.infrastructure.trusted_data.catalog_reader import (
    SqlAlchemyTrustedCatalogReader,
)
from ai_purchase_workflow.infrastructure.trusted_tools import FixtureOrderGateway


def build_prepare_purchase_request(
    repository: PurchaseRequestRepository,
    session: AsyncSession,
) -> PreparePurchaseRequest:
    return PreparePurchaseRequest(
        repository=repository,
        find_vendor=FindVendor(SqlAlchemyTrustedCatalogReader(session), VendorPolicy()),
        create_draft_order=CreateDraftOrder(DraftOrderPolicy()),
        check_budget=CheckBudget(SqlAlchemyBudgetConstraintReader(session), BudgetPolicy()),
    )


def build_submit_purchase_request(
    repository: PurchaseRequestRepository,
) -> SubmitPurchaseRequest:
    return SubmitPurchaseRequest(
        repository=repository,
        submit_order=SubmitOrder(FixtureOrderGateway(), ApprovalGatePolicy()),
    )


def build_approve_purchase_request(
    repository: PurchaseRequestRepository,
    workflow: PurchaseRequestWorkflowGateway,
) -> ApprovePurchaseRequest:
    return ApprovePurchaseRequest(repository, workflow)


def build_reject_purchase_request(
    repository: PurchaseRequestRepository,
    workflow: PurchaseRequestWorkflowGateway,
) -> RejectPurchaseRequest:
    return RejectPurchaseRequest(repository, workflow)


def build_edit_purchase_request(
    repository: PurchaseRequestRepository,
    session: AsyncSession,
) -> EditPurchaseRequest:
    return EditPurchaseRequest(
        repository=repository,
        find_vendor=FindVendor(SqlAlchemyTrustedCatalogReader(session), VendorPolicy()),
        create_draft_order=CreateDraftOrder(DraftOrderPolicy()),
        check_budget=CheckBudget(SqlAlchemyBudgetConstraintReader(session), BudgetPolicy()),
    )
