import uuid
from typing import Callable

import httpx
from fastapi import Depends, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.errors import ForbiddenError, ServiceUnavailableError, UnauthorizedError
from app.core.config import settings
from app.core.db import get_session
from app.models import User
from app.models.enums import Role

# 1. Initialize HTTPBearer scheme
security_scheme = HTTPBearer(auto_error=False)

def get_auth_identity(
    credentials: HTTPAuthorizationCredentials | None = Security(security_scheme),
) -> dict:
    if not credentials or not credentials.credentials:
        raise UnauthorizedError("Missing bearer token")
    
    # HTTPBearer automatically strips out the "Bearer " prefix for you
    token = credentials.credentials
    try:
        res = httpx.get(
            f"{settings.supabase_url}/auth/v1/user",
            headers={"Authorization": f"Bearer {token}", "apikey": settings.supabase_anon_key},
            timeout=10,
        )
    except httpx.HTTPError:
        raise ServiceUnavailableError("Auth service unreachable")
    if res.status_code != 200:
        raise UnauthorizedError("Invalid or expired token")
    return res.json()


def get_current_user(
    identity: dict = Depends(get_auth_identity),
    session: Session = Depends(get_session),
) -> User:
    user = session.scalar(select(User).where(User.auth_id == uuid.UUID(identity["id"])))
    if user is None:
        raise ForbiddenError("Profile not created; call /api/auth/sync")
    return user


def require_role(*roles: Role) -> Callable[..., User]:
    def checker(user: User = Depends(get_current_user)) -> User:
        if user.role not in roles:
            raise ForbiddenError("Not allowed for your role")
        return user

    return checker