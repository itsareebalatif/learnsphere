import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.schemas import UserOut
from app.core.db import get_session
from app.core.security import get_auth_identity, get_current_user
from app.models import User
from app.models.enums import Role

router = APIRouter(prefix="/api", tags=["auth"])


@router.post("/auth/sync", response_model=UserOut)
def sync(identity: dict = Depends(get_auth_identity), session: Session = Depends(get_session)):
    auth_id = uuid.UUID(identity["id"])
    email = identity["email"].lower()
    user = session.scalar(select(User).where(User.auth_id == auth_id))
    if user is None:
        user = session.scalar(select(User).where(User.email == email))
        if user is not None:
            # Only link a pre-created account (e.g. an invited student) to a verified email,
            # otherwise anyone could claim it by signing up with that address.
            if not identity.get("email_confirmed_at"):
                raise HTTPException(status.HTTP_403_FORBIDDEN, "Confirm your email address first")
            user.auth_id = auth_id
        else:
            meta = identity.get("user_metadata") or {}
            user = User(
                auth_id=auth_id,
                email=email,
                full_name=meta.get("full_name") or meta.get("name") or email.split("@")[0],
                role=Role.teacher, 
            )
            session.add(user)
        session.commit()
    return user


@router.get("/me", response_model=UserOut)
def me(user: User = Depends(get_current_user)):
    return user
