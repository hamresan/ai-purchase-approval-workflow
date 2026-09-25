from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from ai_purchase_workflow.application.purchase_requests import PurchaseRequestNotFoundError
from ai_purchase_workflow.domain.purchase_requests import DomainValidationError


def register_purchase_request_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(PurchaseRequestNotFoundError)
    async def handle_not_found(
        _request: Request,
        _error: PurchaseRequestNotFoundError,
    ) -> JSONResponse:
        return JSONResponse(status_code=404, content={"detail": "Purchase request not found."})

    @app.exception_handler(DomainValidationError)
    async def handle_domain_validation(
        _request: Request,
        error: DomainValidationError,
    ) -> JSONResponse:
        return JSONResponse(status_code=422, content={"detail": str(error)})
