import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.User import User


class ParentLink(Base):
    __tablename__ = "parent_links"
    __table_args__ = (
        CheckConstraint("parent_id <> student_id", name="ck_parent_not_self"),
    )

    parent_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.user_id", ondelete="CASCADE"),
        primary_key=True,
    )
    student_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.user_id", ondelete="CASCADE"),
        primary_key=True,
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    parent: Mapped["User"] = relationship(
        foreign_keys=[parent_id], back_populates="child_links"
    )
    student: Mapped["User"] = relationship(
        foreign_keys=[student_id], back_populates="parent_links"
    )

    def __repr__(self) -> str:
        return f"<ParentLink parent={self.parent_id} student={self.student_id}>"
