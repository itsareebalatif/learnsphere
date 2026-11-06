from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session

from app.auth import service
from app.auth.schemas import AuthSessionOut, RefreshIn, SignupOut, UserLoginIn, UserOut, UserSignupIn
from app.core.db import get_session
from app.core.security import get_auth_identity, get_current_user
from app.models import User

router = APIRouter(prefix="/api", tags=["auth"])


@router.post("/auth/login", response_model=AuthSessionOut)
def login(data: UserLoginIn, session: Session = Depends(get_session)):
    return service.login_user(session, data)


@router.post("/auth/signup", response_model=SignupOut)
def signup(data: UserSignupIn, session: Session = Depends(get_session)):
    return service.signup_user(session, data)


# @router.post("/auth/logout")
# def logout(authorization: str | None = Header(default=None)):
#     service.logout_user(authorization)
#     return {"detail": "Logged out"}

from fastapi import APIRouter, Depends, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from app.auth import service
security_scheme = HTTPBearer(auto_error=False)
@router.post("/logout")
def logout(credentials: HTTPAuthorizationCredentials | None = Security(security_scheme)):
    if not credentials or not credentials.credentials:
        raise UnauthorizedError("Missing bearer token")
    
    # Reconstruct the "Bearer <token>" string for service layer, or pass credentials.credentials directly
    authorization_header = f"Bearer {credentials.credentials}"
    service.logout_user(authorization_header)
    return {"message": "Successfully logged out"}

@router.post("/auth/refresh", response_model=AuthSessionOut)
def refresh(data: RefreshIn, session: Session = Depends(get_session)):
    return service.refresh_user(session, data)


@router.post("/auth/sync", response_model=UserOut)
def sync(identity: dict = Depends(get_auth_identity), session: Session = Depends(get_session)):
    return service.sync_user(session, identity)


@router.get("/me", response_model=UserOut)
def me(user: User = Depends(get_current_user)):
    return user
