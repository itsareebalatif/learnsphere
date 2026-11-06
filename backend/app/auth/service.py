import logging
import uuid

import httpx
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.auth.schemas import AuthSessionOut, RefreshIn, SignupOut, UserLoginIn, UserOut, UserSignupIn
from app.core.config import settings
from app.core.errors import (
    BadRequestError,
    ConflictError,
    ForbiddenError,
    ServiceUnavailableError,
    UnauthorizedError,
)
from app.models import User
from app.models.enums import Role

logger = logging.getLogger(__name__)

def sync_user(session: Session, identity: dict) -> User:
    raw_id = identity.get("id")
    raw_email = identity.get("email")
    
    if not raw_id or not raw_email:
        raise BadRequestError("Invalid authentication payload structure.")
        
    try:
        auth_id = uuid.UUID(str(raw_id))
        email = str(raw_email).strip().lower()
    except (ValueError, AttributeError) as e:
        logger.error(f"Malformed auth fields: {e}")
        raise BadRequestError("Invalid identity metadata format.")

    try:
        
        user = session.scalar(select(User).where(User.auth_id == auth_id))
        if user is not None:
            return user

       
        user = session.scalar(select(User).where(User.email == email))
        if user is not None:
            _link_precreated_user(session, user, auth_id, identity)
        
        else:
            user = _create_teacher(session, auth_id, email, identity)
        
        session.commit()
        return user

    except Exception as e:
        session.rollback()
        logger.warning(f"Sync user failed, transaction rolled back. Reason: {e}")
        raise


def _link_precreated_user(session: Session, user: User, auth_id: uuid.UUID, identity: dict) -> None:
    # Only Supabase's own field counts. Never read this from user_metadata: users can
    # write anything they like there when they sign up.
    if not identity.get("email_confirmed_at"):
        logger.warning(f"Link blocked: unverified email for user {user.user_id}")
        raise ForbiddenError("Confirm your email address first")

    try:
        if not isinstance(auth_id, uuid.UUID):
            auth_id = uuid.UUID(str(auth_id))
            
        user.auth_id = auth_id
        
        
        session.flush() 
        
    except ValueError:
        logger.error(f"Malformed auth_id provided to linker: {auth_id}")
        raise BadRequestError("Invalid authentication identifier format.")
        
    except IntegrityError as e:
        # Triggers if another account already snagged this auth_id
        logger.critical(f"Database conflict linking auth_id {auth_id}: {e}")
        raise ConflictError("This authentication ID is already linked to another profile.")


def _create_teacher(session: Session, auth_id: uuid.UUID, email: str, identity: dict) -> User:
    meta = identity.get("user_metadata") or {}
    user = User(
        auth_id=auth_id,
        email=email,
        full_name=meta.get("full_name") or meta.get("name") or email.split("@")[0],
        role=Role.teacher,  # FR-1: self sign-up is a teacher; others come via invite
    )
    session.add(user)
    return user




def _call_supabase_auth(
    path: str, payload: dict, params: dict | None = None, token: str | None = None
) -> httpx.Response:
    headers = {"apikey": settings.supabase_anon_key}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    try:
        res = httpx.post(
            f"{settings.supabase_url}/auth/v1/{path}",
            params=params,
            json=payload,
            headers=headers,
            timeout=10,
        )
    except httpx.HTTPError as exc:
        raise ServiceUnavailableError("Auth service unreachable") from exc
    if res.status_code == 429:
        raise ServiceUnavailableError("Too many attempts, please wait a minute")
    return res


def _error_body(res: httpx.Response) -> dict:
    try:
        body = res.json()
    except ValueError:
        return {}
    return body if isinstance(body, dict) else {}


def _session_out(session: Session, body: dict) -> AuthSessionOut:
    """Turn Supabase's token response into ours, creating or linking our users row."""
    user = sync_user(session, body["user"])
    return AuthSessionOut(
        access_token=body["access_token"],
        refresh_token=body["refresh_token"],
        expires_in=body.get("expires_in", 3600),
        user=UserOut.model_validate(user),
    )


def login_user(session: Session, data: UserLoginIn) -> AuthSessionOut:
    res = _call_supabase_auth(
        "token", {"email": data.email, "password": data.password}, {"grant_type": "password"}
    )
    if res.status_code != 200:
        if _error_body(res).get("error_code") == "email_not_confirmed":
            raise ForbiddenError("Confirm your email address first")
        if res.status_code in (400, 401, 422):  
            raise UnauthorizedError("Wrong email or password")
        raise ServiceUnavailableError("Sign-in is unavailable, please try again")
    return _session_out(session, res.json())


def signup_user(session: Session, data: UserSignupIn) -> SignupOut:
    origins = settings.cors_origins
    res = _call_supabase_auth(
        "signup",
        {"email": data.email, "password": data.password, "data": {"full_name": data.full_name.strip()}},
        {"redirect_to": origins[0]} if origins else None,  # where the confirmation link sends them
    )
    if res.status_code in (400, 422):
        body = _error_body(res)
        raise BadRequestError(body.get("msg") or body.get("error_description") or "Could not sign up")
    if res.status_code != 200:
        raise ServiceUnavailableError("Sign-up is unavailable, please try again")

    body = res.json()
    if body.get("access_token"):  # email confirmation is switched off in Supabase: already logged in
        return SignupOut(confirm_email=False, session=_session_out(session, body))
    # Confirmation needed: no session yet. Our users row is created on their first login.
    return SignupOut(confirm_email=True)


def logout_user(authorization: str | None) -> None:
    """End this device's session at Supabase (its refresh token stops working)."""
    if not authorization or not authorization.lower().startswith("bearer "):
        raise UnauthorizedError("Missing bearer token")
    token = authorization.split(" ", 1)[1].strip()
    res = _call_supabase_auth("logout", {}, {"scope": "local"}, token)
    # 401/403/404: the token is already expired or revoked, so there is nothing left to end.
    if res.status_code not in (200, 204, 401, 403, 404):
        raise ServiceUnavailableError("Could not log out, please try again")


def refresh_user(session: Session, data: RefreshIn) -> AuthSessionOut:
    res = _call_supabase_auth(
        "token", {"refresh_token": data.refresh_token}, {"grant_type": "refresh_token"}
    )
    if res.status_code != 200:
        if res.status_code in (400, 401, 403, 422):  # invalid, used or expired refresh token
            raise UnauthorizedError("Session expired, please log in again")
        raise ServiceUnavailableError("Could not refresh the session, please try again")
    return _session_out(session, res.json())
