import uuid

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Organisation, User
from app.models.enums import Role
from app.schools.schemas import InviteIn, SchoolCreate, SchoolUserOut

INVITABLE_ROLES = {Role.teacher, Role.student, Role.parent}


def create_school(session: Session, admin: User, data: SchoolCreate) -> Organisation:
    if admin.org_id is not None:
        raise HTTPException(status.HTTP_409_CONFLICT, "You already belong to a school")
    org = Organisation(name=data.name.strip(), type=data.type, region=data.region)
    session.add(org)
    session.flush()
    admin.org_id = org.org_id
    session.commit()
    return org


def get_school(session: Session, org_id: uuid.UUID | None) -> Organisation:
    org = session.get(Organisation, org_id) if org_id else None
    if org is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "You have not created a school yet")
    return org


def list_users(session: Session, org_id: uuid.UUID) -> list[SchoolUserOut]:
    users = session.scalars(
        select(User).where(User.org_id == org_id).order_by(User.role, User.full_name)
    ).all()
    return [
        SchoolUserOut(
            user_id=u.user_id, email=u.email, full_name=u.full_name,
            role=u.role, joined=u.auth_id is not None,
        )
        for u in users
    ]


def invite_user(session: Session, admin: User, data: InviteIn) -> SchoolUserOut:
    """Pre-create a user row; it is linked to their login the first time they sign in."""
    if admin.org_id is None:
        raise HTTPException(status.HTTP_409_CONFLICT, "Create your school first")
    if data.role not in INVITABLE_ROLES:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Role must be teacher, student or parent")
    email = data.email.lower()
    if session.scalar(select(User).where(User.email == email)) is not None:
        raise HTTPException(status.HTTP_409_CONFLICT, "That email is already registered")
    user = User(email=email, full_name=data.full_name.strip(), role=data.role, org_id=admin.org_id)
    session.add(user)
    session.commit()
    return SchoolUserOut(
        user_id=user.user_id, email=user.email, full_name=user.full_name, role=user.role, joined=False
    )
