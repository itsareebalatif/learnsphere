import uuid

from fastapi import APIRouter, Depends, File, Response, UploadFile
from sqlalchemy.orm import Session

from app.core.db import get_session
from app.core.security import require_role
from app.courses import service
from app.courses.schemas import CourseCreate, CourseOut, FileOut
from app.models import User
from app.models.enums import Role

# router = APIRouter(prefix="/api/courses", tags=["courses"])

# teacher_only = require_role(Role.teacher)


# @router.post("", response_model=CourseOut)
# def create_course(
#     data: CourseCreate, teacher: User = Depends(teacher_only), session: Session = Depends(get_session)
# ):
#     return service.create_course(session, teacher, data)


# @router.get("", response_model=list[CourseOut])
# def list_courses(teacher: User = Depends(teacher_only), session: Session = Depends(get_session)):
#     return service.list_courses(session, teacher)


# @router.get("/{course_id}", response_model=CourseOut)
# def get_course(
#     course_id: uuid.UUID, teacher: User = Depends(teacher_only), session: Session = Depends(get_session)
# ):
#     return service.get_course(session, teacher, course_id)


# @router.get("/{course_id}/files", response_model=list[FileOut])
# def list_files(
#     course_id: uuid.UUID, teacher: User = Depends(teacher_only), session: Session = Depends(get_session)
# ):
#     return service.list_files(session, teacher, course_id)


# @router.post("/{course_id}/files", response_model=FileOut)
# def upload_file(
#     course_id: uuid.UUID,
#     file: UploadFile = File(...),
#     teacher: User = Depends(teacher_only),
#     session: Session = Depends(get_session),
# ):
#     return service.upload_file(session, teacher, course_id, file)


# @router.delete("/{course_id}/files/{file_id}", status_code=204)
# def delete_file(
#     course_id: uuid.UUID,
#     file_id: uuid.UUID,
#     teacher: User = Depends(teacher_only),
#     session: Session = Depends(get_session),
# ):
#     service.delete_file(session, teacher, course_id, file_id)
#     return Response(status_code=204)
