import uuid

from pydantic import BaseModel

from app.models.enums import Role


class UserOut(BaseModel):
    user_id: uuid.UUID
    email: str
    full_name: str
    role: Role
    org_id: uuid.UUID | None

    model_config = {"from_attributes": True}
