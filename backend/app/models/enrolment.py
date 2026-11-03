import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Numeric, String, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.school_class import SchoolClass
    from app.models.user import User


class Enrolment(Base):
    """A student joined to a class, with their progress."""

    __tablename__ = "enrolments"
    __table_args__ = (UniqueConstraint("class_id", "student_id", name="uq_enrolment_class_student"),)

    enrolment_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    class_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("classes.class_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    student_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.user_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="active")
    progress_pct: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False, default=0)
    enrolled_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    school_class: Mapped["SchoolClass"] = relationship(back_populates="enrolments")
    student: Mapped["User"] = relationship()
