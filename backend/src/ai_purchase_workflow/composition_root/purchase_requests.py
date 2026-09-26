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
from ai_purchase_workflow.infrastructure.trusted_tools import (
    FixtureBudgetReader,
    FixtureCatalogReader,
    FixtureOrderGateway,
)


def build_prepare_purchase_request(
    repository: PurchaseRequestRepository,
) -> PreparePurchaseRequest:
    return PreparePurchaseRequest(
        repository=repository,
        find_vendor=FindVendor(FixtureCatalogReader(), VendorPolicy()),
        create_draft_order=CreateDraftOrder(DraftOrderPolicy()),
        check_budget=CheckBudget(FixtureBudgetReader(), BudgetPolicy()),
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
) -> EditPurchaseRequest:
    return EditPurchaseRequest(
        repository=repository,
        find_vendor=FindVendor(FixtureCatalogReader(), VendorPolicy()),
        create_draft_order=CreateDraftOrder(DraftOrderPolicy()),
        check_budget=CheckBudget(FixtureBudgetReader(), BudgetPolicy()),
    )
