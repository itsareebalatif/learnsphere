import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field

from app.models.enums import OrgType, Region, Role


class SchoolCreate(BaseModel):
    name: str = Field(min_length=2, max_length=150)
    type: OrgType = OrgType.school
    region: Region = Region.eu


class SchoolOut(BaseModel):
    org_id: uuid.UUID
    name: str
    type: OrgType
    region: Region
    created_at: datetime

    model_config = {"from_attributes": True}


class InviteIn(BaseModel):
    email: EmailStr
    full_name: str = Field(min_length=1, max_length=120)
    role: Role


class SchoolUserOut(BaseModel):
    user_id: uuid.UUID
    email: str
    full_name: str
    role: Role
    joined: bool  # True once the person has logged in at least once

    model_config = {"from_attributes": True}
