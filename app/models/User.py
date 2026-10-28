import uuid
from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import DateTime, Enum, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.enums import Role

if TYPE_CHECKING:
    from app.models.organisation import Organisation
    from app.models.parent_link import ParentLink


class User(Base):
    __tablename__ = "users"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    # Nullable so a teacher can sign up alone before joining a school (FR-1)
    org_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organisations.org_id", ondelete="CASCADE"),
        index=True,
    )
    full_name: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[Role] = mapped_column(Enum(Role, name="user_role"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    organisation: Mapped[Optional["Organisation"]] = relationship(
        back_populates="users"
    )
    # Links where this user is the parent / the student
    child_links: Mapped[List["ParentLink"]] = relationship(
        foreign_keys="ParentLink.parent_id",
        back_populates="parent",
        cascade="all, delete-orphan",
    )
    parent_links: Mapped[List["ParentLink"]] = relationship(
        foreign_keys="ParentLink.student_id",
        back_populates="student",
        cascade="all, delete-orphan",
    )

    @property
    def children(self) -> List["User"]:
        return [link.student for link in self.child_links]

    @property
    def parents(self) -> List["User"]:
        return [link.parent for link in self.parent_links]

    def __repr__(self) -> str:
        return f"<User {self.email!r} ({self.role.value})>"
