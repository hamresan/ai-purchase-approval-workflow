from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query

from ai_purchase_workflow.application.purchase_requests import (
    CreatePurchaseRequest,
    GetPurchaseRequest,
    ListPurchaseRequests,
)
from ai_purchase_workflow.domain.purchase_requests import RequestStatus
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
RequestStatusQuery = Annotated[RequestStatus | None, Query(alias="status")]


@router.post("", response_model=PurchaseRequestResponse, status_code=201)
async def create_purchase_request(
    body: CreatePurchaseRequestBody,
    use_case: CreatePurchaseRequestDependency,
) -> PurchaseRequestResponse:
    view = await use_case.execute(PurchaseRequestCommandMapper.from_body(body))
    return PurchaseRequestResponse.from_view(view)


@router.get("/{request_id}", response_model=PurchaseRequestResponse)
async def get_purchase_request_by_id(
    request_id: UUID,
    use_case: GetPurchaseRequestDependency,
) -> PurchaseRequestResponse:
    view = await use_case.execute(request_id)
    return PurchaseRequestResponse.from_view(view)


@router.get("", response_model=list[PurchaseRequestResponse])
async def list_purchase_requests(
    use_case: ListPurchaseRequestsDependency,
    request_status: RequestStatusQuery = None,
) -> list[PurchaseRequestResponse]:
    views = await use_case.execute(status=request_status)
    return [PurchaseRequestResponse.from_view(view) for view in views]
