import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from app.models.enums import CourseStatus, FileStatus


class CourseCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    subject: str | None = Field(default=None, max_length=80)


class CourseOut(BaseModel):
    course_id: uuid.UUID
    title: str
    subject: str | None
    status: CourseStatus
    version: int
    file_count: int
    created_at: datetime


class FileOut(BaseModel):
    file_id: uuid.UUID
    file_name: str
    file_type: str
    status: FileStatus
    error_message: str | None
    uploaded_at: datetime

    model_config = {"from_attributes": True}
