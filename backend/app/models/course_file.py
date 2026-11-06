import uuid
from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import DateTime, Enum, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.enums import FileStatus

if TYPE_CHECKING:
    from app.models.content_chunk import ContentChunk
    from app.models.course import Course


class CourseFile(Base):
    """A file the teacher uploaded (PDF, slides, Word, video)."""

    __tablename__ = "course_files"

    file_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    course_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("courses.course_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    file_type: Mapped[str] = mapped_column(String(20), nullable=False)  # pdf, pptx, docx, video
    file_url: Mapped[Optional[str]] = mapped_column(Text)  # path in Supabase Storage
    status: Mapped[FileStatus] = mapped_column(
        Enum(FileStatus, name="file_status"), nullable=False, default=FileStatus.uploaded
    )
    error_message: Mapped[Optional[str]] = mapped_column(Text)  # why processing failed
    uploaded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    course: Mapped["Course"] = relationship(back_populates="files")
    chunks: Mapped[List["ContentChunk"]] = relationship(
        back_populates="file", cascade="all, delete-orphan"
    )
