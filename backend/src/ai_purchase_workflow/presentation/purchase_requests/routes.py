from typing import Annotated, Literal
from uuid import UUID

from fastapi import APIRouter, Depends, Header, Query

from ai_purchase_workflow.application.purchase_requests import (
    CreatePurchaseRequest,
    GetPurchaseRequest,
    ListPurchaseRequests,
    PreparePurchaseRequest,
    PurchaseRequestListQuery,
    SubmitPurchaseRequest,
)
from ai_purchase_workflow.domain.purchase_requests import RequestStatus
from ai_purchase_workflow.presentation.purchase_requests.approval_dispatcher import (
    ApprovalActionDispatcher,
)
from ai_purchase_workflow.presentation.purchase_requests.dependencies import (
    get_approval_dispatcher,
    get_create_purchase_request,
    get_list_purchase_requests,
    get_prepare_purchase_request,
    get_purchase_request,
    get_submit_purchase_request,
)
from ai_purchase_workflow.presentation.purchase_requests.mappers import PurchaseRequestCommandMapper
from ai_purchase_workflow.presentation.purchase_requests.schemas import (
    ApprovalBody,
    CreatePurchaseRequestBody,
    PurchaseRequestListResponse,
    PurchaseRequestResponse,
)

router = APIRouter(prefix="/api/purchase-requests", tags=["purchase-requests"])

CreatePurchaseRequestDependency = Annotated[
    CreatePurchaseRequest,
    Depends(get_create_purchase_request),
]
GetPurchaseRequestDependency = Annotated[
    GetPurchaseRequest,
    Depends(get_purchase_request),
]
ListPurchaseRequestsDependency = Annotated[
    ListPurchaseRequests,
    Depends(get_list_purchase_requests),
]
PreparePurchaseRequestDependency = Annotated[
    PreparePurchaseRequest,
    Depends(get_prepare_purchase_request),
]
SubmitPurchaseRequestDependency = Annotated[
    SubmitPurchaseRequest,
    Depends(get_submit_purchase_request),
]
ApprovalDispatcherDependency = Annotated[
    ApprovalActionDispatcher,
    Depends(get_approval_dispatcher),
]
RequestStatusQuery = Annotated[RequestStatus | None, Query(alias="status")]
LimitQuery = Annotated[int, Query(ge=1, le=100)]
OffsetQuery = Annotated[int, Query(ge=0)]
OrderQuery = Annotated[Literal["asc", "desc"], Query()]
IdempotencyKeyHeader = Annotated[str | None, Header(alias="Idempotency-Key", min_length=1, max_length=200)]


@router.post("", response_model=PurchaseRequestResponse, status_code=201)
async def create_purchase_request(
    body: CreatePurchaseRequestBody,
    use_case: CreatePurchaseRequestDependency,
    idempotency_key: IdempotencyKeyHeader = None,
) -> PurchaseRequestResponse:
    view = await use_case.execute(
        PurchaseRequestCommandMapper.from_body(body),
        idempotency_key=idempotency_key,
    )
    return PurchaseRequestResponse.from_view(view)


@router.get("/{request_id}", response_model=PurchaseRequestResponse)
async def get_purchase_request_by_id(
    request_id: UUID,
    use_case: GetPurchaseRequestDependency,
) -> PurchaseRequestResponse:
    view = await use_case.execute(request_id)
    return PurchaseRequestResponse.from_view(view)


@router.get("", response_model=PurchaseRequestListResponse)
async def list_purchase_requests(
    use_case: ListPurchaseRequestsDependency,
    request_status: RequestStatusQuery = None,
    limit: LimitQuery = 20,
    offset: OffsetQuery = 0,
    order: OrderQuery = "desc",
) -> PurchaseRequestListResponse:
    page = await use_case.execute(
        PurchaseRequestListQuery(
            status=request_status,
            limit=limit,
            offset=offset,
            descending=order == "desc",
        )
    )
    return PurchaseRequestListResponse(
        items=[PurchaseRequestResponse.from_view(view) for view in page.items],
        total=page.total,
        limit=page.limit,
        offset=page.offset,
    )


@router.post("/{request_id}/prepare", response_model=PurchaseRequestResponse)
async def prepare_purchase_request(
    request_id: UUID,
    use_case: PreparePurchaseRequestDependency,
) -> PurchaseRequestResponse:
    view = await use_case.execute(request_id)
    return PurchaseRequestResponse.from_view(view)


@router.post("/{request_id}/submit", response_model=PurchaseRequestResponse)
async def submit_purchase_request(
    request_id: UUID,
    use_case: SubmitPurchaseRequestDependency,
) -> PurchaseRequestResponse:
    view = await use_case.execute(request_id)
    return PurchaseRequestResponse.from_view(view)


@router.post("/{request_id}/approval", response_model=PurchaseRequestResponse)
async def decide_purchase_request(
    request_id: UUID,
    body: ApprovalBody,
    dispatcher: ApprovalDispatcherDependency,
) -> PurchaseRequestResponse:
    view = await dispatcher.execute(request_id, body)
    return PurchaseRequestResponse.from_view(view)
