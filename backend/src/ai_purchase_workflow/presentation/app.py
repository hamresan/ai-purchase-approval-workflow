from fastapi import FastAPI

from ai_purchase_workflow.composition_root.settings import Settings, get_settings
from ai_purchase_workflow.infrastructure.persistence import create_session_factory
from ai_purchase_workflow.presentation.purchase_requests import router as purchase_requests_router
from ai_purchase_workflow.presentation.purchase_requests.error_handlers import (
    register_purchase_request_error_handlers,
)
from ai_purchase_workflow.presentation.routes import health_router


def create_app(settings: Settings | None = None) -> FastAPI:
    resolved_settings = settings or get_settings()
    app = FastAPI(title="AI Purchase Approval Workflow")
    app.state.settings = resolved_settings
    app.state.session_factory = create_session_factory(resolved_settings.database_url)
    register_purchase_request_error_handlers(app)
    app.include_router(health_router)
    app.include_router(purchase_requests_router)
    return app
