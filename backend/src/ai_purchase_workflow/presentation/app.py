from fastapi import FastAPI

from ai_purchase_workflow.composition_root.settings import Settings, get_settings
from ai_purchase_workflow.presentation.routes import health_router


def create_app(settings: Settings | None = None) -> FastAPI:
    resolved_settings = settings or get_settings()
    app = FastAPI(title="AI Purchase Approval Workflow")
    app.state.settings = resolved_settings
    app.include_router(health_router)
    return app
