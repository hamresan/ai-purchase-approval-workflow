from ai_purchase_workflow.application.purchase_requests import (
    CheckBudget,
    CreateDraftOrder,
    FindVendor,
    PreparePurchaseRequest,
    PurchaseRequestRepository,
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
