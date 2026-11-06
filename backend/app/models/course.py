import uuid
from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.enums import CourseStatus

if TYPE_CHECKING:
    from app.models.course_file import CourseFile


class Course(Base):
    """A course created by a teacher (draft or published)."""

    __tablename__ = "courses"

    course_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    # Nullable: a teacher who signed up alone has no school yet (FR-1)
    org_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organisations.org_id", ondelete="CASCADE"),
        index=True,
    )
    teacher_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.user_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    subject: Mapped[Optional[str]] = mapped_column(String(80))
    status: Mapped[CourseStatus] = mapped_column(
        Enum(CourseStatus, name="course_status"), nullable=False, default=CourseStatus.draft
    )
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    files: Mapped[List["CourseFile"]] = relationship(
        back_populates="course", cascade="all, delete-orphan"
    )
