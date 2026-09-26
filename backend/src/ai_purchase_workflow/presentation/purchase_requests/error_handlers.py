from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

from ai_purchase_workflow.application.purchase_requests import (
    PurchaseRequestApprovalError,
    PurchaseRequestNotFoundError,
)
from ai_purchase_workflow.domain.purchase_requests import DomainValidationError


def register_purchase_request_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(PurchaseRequestNotFoundError)
    async def handle_not_found(
        _request: Request,
        _error: PurchaseRequestNotFoundError,
    ) -> JSONResponse:
        return JSONResponse(status_code=404, content={"detail": "Purchase request not found."})

    @app.exception_handler(PurchaseRequestApprovalError)
    async def handle_approval_conflict(
        _request: Request,
        error: PurchaseRequestApprovalError,
    ) -> JSONResponse:
        return JSONResponse(status_code=409, content={"detail": str(error)})

    @app.exception_handler(DomainValidationError)
    async def handle_domain_validation(
        _request: Request,
        error: DomainValidationError,
    ) -> JSONResponse:
        return JSONResponse(status_code=422, content={"detail": str(error)})

    @app.exception_handler(SQLAlchemyError)
    async def handle_persistence_error(
        _request: Request,
        _error: SQLAlchemyError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=503,
            content={"detail": "The service is temporarily unavailable."},
        )

    @app.exception_handler(Exception)
    async def handle_unexpected_error(
        _request: Request,
        _error: Exception,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=500,
            content={"detail": "An unexpected server error occurred."},
        )
