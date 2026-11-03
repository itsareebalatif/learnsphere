from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.db import get_session
from app.core.security import require_role
from app.models import User
from app.models.enums import Role
from app.schools import service
from app.schools.schemas import InviteIn, SchoolCreate, SchoolOut, SchoolUserOut

router = APIRouter(prefix="/api/schools", tags=["schools"])

admin_only = require_role(Role.admin)


@router.post("", response_model=SchoolOut, status_code=status.HTTP_201_CREATED)
def create_school(
    data: SchoolCreate, admin: User = Depends(admin_only), session: Session = Depends(get_session)
):
    return service.create_school(session, admin, data)


@router.get("/me", response_model=SchoolOut)
def my_school(admin: User = Depends(admin_only), session: Session = Depends(get_session)):
    return service.get_school(session, admin.org_id)


@router.get("/me/users", response_model=list[SchoolUserOut])
def school_users(admin: User = Depends(admin_only), session: Session = Depends(get_session)):
    service.get_school(session, admin.org_id)
    return service.list_users(session, admin.org_id)


@router.post("/me/users", response_model=SchoolUserOut, status_code=status.HTTP_201_CREATED)
def invite_user(
    data: InviteIn, admin: User = Depends(admin_only), session: Session = Depends(get_session)
):
    return service.invite_user(session, admin, data)
