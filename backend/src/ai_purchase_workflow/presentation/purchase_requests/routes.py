from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status

from ai_purchase_workflow.application.purchase_requests import (
    CreatePurchaseRequest,
    GetPurchaseRequest,
    ListPurchaseRequests,
)
from ai_purchase_workflow.application.purchase_requests.use_cases import PurchaseRequestNotFoundError
from ai_purchase_workflow.domain.purchase_requests import DomainValidationError, RequestStatus
from ai_purchase_workflow.presentation.purchase_requests.dependencies import (
    get_create_purchase_request,
    get_list_purchase_requests,
    get_purchase_request,
)
from ai_purchase_workflow.presentation.purchase_requests.mappers import PurchaseRequestCommandMapper
from ai_purchase_workflow.presentation.purchase_requests.schemas import (
    CreatePurchaseRequestBody,
    PurchaseRequestResponse,
)

router = APIRouter(prefix="/api/purchase-requests", tags=["purchase-requests"])


@router.post("", response_model=PurchaseRequestResponse, status_code=status.HTTP_201_CREATED)
async def create_purchase_request(
    body: CreatePurchaseRequestBody,
    use_case: CreatePurchaseRequest = Depends(get_create_purchase_request),
) -> PurchaseRequestResponse:
    try:
        view = await use_case.execute(PurchaseRequestCommandMapper.from_body(body))
    except DomainValidationError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc
    return PurchaseRequestResponse.from_view(view)


@router.get("/{request_id}", response_model=PurchaseRequestResponse)
async def get_purchase_request_by_id(
    request_id: UUID,
    use_case: GetPurchaseRequest = Depends(get_purchase_request),
) -> PurchaseRequestResponse:
    try:
        view = await use_case.execute(request_id)
    except PurchaseRequestNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Purchase request not found.") from exc
    return PurchaseRequestResponse.from_view(view)


@router.get("", response_model=list[PurchaseRequestResponse])
async def list_purchase_requests(
    request_status: RequestStatus | None = Query(default=None, alias="status"),
    use_case: ListPurchaseRequests = Depends(get_list_purchase_requests),
) -> list[PurchaseRequestResponse]:
    views = await use_case.execute(status=request_status)
    return [PurchaseRequestResponse.from_view(view) for view in views]
