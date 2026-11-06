import uuid

from pydantic import BaseModel, EmailStr, Field

from app.models.enums import Role


class UserOut(BaseModel):
    user_id: uuid.UUID
    email: str
    full_name: str
    role: Role
    org_id: uuid.UUID | None

    model_config = {"from_attributes": True}


class UserLoginIn(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


class UserSignupIn(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    full_name: str = Field(min_length=1, max_length=120)


class RefreshIn(BaseModel):
    refresh_token: str = Field(min_length=1)


class AuthSessionOut(BaseModel):
    """Supabase session tokens plus our own user row, so the browser can keep the session."""

    access_token: str
    refresh_token: str
    expires_in: int
    user: UserOut


class SignupOut(BaseModel):
    confirm_email: bool  # True: a confirmation email was sent, no session yet
    session: AuthSessionOut | None = None
