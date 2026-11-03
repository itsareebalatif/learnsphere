import uuid
from typing import Callable

import httpx
from fastapi import Depends, Header, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.db import get_session
from app.models import User
from app.models.enums import Role


def get_auth_identity(authorization: str | None = Header(default=None)) -> dict:

    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Missing bearer token")
    token = authorization.split(" ", 1)[1].strip()
    try:
        res = httpx.get(
            f"{settings.supabase_url}/auth/v1/user",
            headers={"Authorization": f"Bearer {token}", "apikey": settings.supabase_anon_key},
            timeout=10,
        )
    except httpx.HTTPError:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, "Auth service unreachable")
    if res.status_code != 200:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid or expired token")
    return res.json()


def get_current_user(
    identity: dict = Depends(get_auth_identity),
    session: Session = Depends(get_session),
) -> User:
    user = session.scalar(select(User).where(User.auth_id == uuid.UUID(identity["id"])))
    if user is None:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Profile not created; call /api/auth/sync")
    return user


def require_role(*roles: Role) -> Callable[..., User]:
    def checker(user: User = Depends(get_current_user)) -> User:
        if user.role not in roles:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Not allowed for your role")
        return user

    return checker
