import uuid
from typing import TYPE_CHECKING, Optional

from pgvector.sqlalchemy import Vector
from sqlalchemy import ForeignKey, Index, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.course_file import CourseFile

EMBEDDING_DIM = 384  # bge-small


class ContentChunk(Base):
    """A small piece of a file's text plus its embedding, used by the AI to search the course."""

    __tablename__ = "content_chunks"
    __table_args__ = (
        # Vector index so "find the 5 most similar chunks" stays fast (cosine distance).
        Index(
            "ix_content_chunks_embedding",
            "embedding",
            postgresql_using="hnsw",
            postgresql_ops={"embedding": "vector_cosine_ops"},
        ),
    )

    chunk_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    file_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("course_files.file_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    chunk_text: Mapped[str] = mapped_column(Text, nullable=False)
    # Where it came from, e.g. "page 4", "slide 12" or "03:15" for video
    source_ref: Mapped[Optional[str]] = mapped_column(String(20))
    embedding: Mapped[Optional[list[float]]] = mapped_column(Vector(EMBEDDING_DIM))

    file: Mapped["CourseFile"] = relationship(back_populates="chunks")
