import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class ClassCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    term: str | None = Field(default=None, max_length=20)


class ClassOut(BaseModel):
    class_id: uuid.UUID
    name: str
    term: str | None
    teacher_name: str
    student_count: int
    created_at: datetime


class AddStudentIn(BaseModel):
    email: EmailStr
    full_name: str | None = Field(default=None, max_length=120)  # used only if the student is new


class StudentOut(BaseModel):
    user_id: uuid.UUID
    email: str
    full_name: str
    joined: bool  # True once the student has logged in at least once
