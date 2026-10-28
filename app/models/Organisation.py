import uuid
from datetime import datetime
from typing import TYPE_CHECKING, List

from sqlalchemy import DateTime, Enum, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.enums import OrgType, Region

if TYPE_CHECKING:
    from app.models.user import User


class Organisation(Base):
    __tablename__ = "organisations"

    org_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    type: Mapped[OrgType] = mapped_column(
        Enum(OrgType, name="org_type"), nullable=False
    )
    region: Mapped[Region] = mapped_column(
        Enum(Region, name="region"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    users: Mapped[List["User"]] = relationship(back_populates="organisation")

    def __repr__(self) -> str:
        return f"<Organisation {self.name!r} ({self.type.value})>"
