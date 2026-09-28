from uuid import UUID

from sqlalchemy import String
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from ai_purchase_workflow.infrastructure.persistence.models import Base


class ApplicationUserRoleModel(Base):
    __tablename__ = "application_user_roles"

    user_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True)
    role: Mapped[str] = mapped_column(String(30), primary_key=True)
