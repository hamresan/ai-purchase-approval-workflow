import logging
from time import perf_counter
from uuid import uuid4

from fastapi import FastAPI, Request

logger = logging.getLogger("ai_purchase_workflow.http")


def register_http_observability(app: FastAPI) -> None:
    @app.middleware("http")
    async def observe_request(request: Request, call_next):
        request_id = request.headers.get("X-Request-ID") or str(uuid4())
        started = perf_counter()
        try:
            response = await call_next(request)
        except Exception:
            duration_ms = round((perf_counter() - started) * 1000, 2)
            logger.exception(
                "http_request_failed",
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "path": request.url.path,
                    "duration_ms": duration_ms,
                },
            )
            raise

        duration_ms = round((perf_counter() - started) * 1000, 2)
        response.headers["X-Request-ID"] = request_id
        logger.info(
            "http_request_completed",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "duration_ms": duration_ms,
            },
        )
        return response
