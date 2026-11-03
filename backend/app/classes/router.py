import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.classes import service
from app.classes.schemas import AddStudentIn, ClassCreate, ClassOut, StudentOut
from app.core.db import get_session
from app.core.security import require_role
from app.models import User
from app.models.enums import Role

router = APIRouter(prefix="/api/classes", tags=["classes"])

teacher_only = require_role(Role.teacher)


@router.post("", response_model=ClassOut, status_code=status.HTTP_201_CREATED)
def create_class(
    data: ClassCreate, teacher: User = Depends(teacher_only), session: Session = Depends(get_session)
):
    return service.create_class(session, teacher, data)


@router.get("", response_model=list[ClassOut])
def list_my_classes(
    user: User = Depends(require_role(Role.teacher, Role.student)),
    session: Session = Depends(get_session),
):
    return service.list_my_classes(session, user)


@router.get("/{class_id}", response_model=ClassOut)
def get_class(
    class_id: uuid.UUID, teacher: User = Depends(teacher_only), session: Session = Depends(get_session)
):
    return service.get_class_out(session, teacher, class_id)


@router.get("/{class_id}/students", response_model=list[StudentOut])
def list_students(
    class_id: uuid.UUID, teacher: User = Depends(teacher_only), session: Session = Depends(get_session)
):
    return service.list_students(session, teacher, class_id)


@router.post("/{class_id}/students", response_model=StudentOut, status_code=status.HTTP_201_CREATED)
def add_student(
    class_id: uuid.UUID,
    data: AddStudentIn,
    teacher: User = Depends(teacher_only),
    session: Session = Depends(get_session),
):
    return service.add_student(session, teacher, class_id, data)
