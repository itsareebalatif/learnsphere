import enum


class OrgType(str, enum.Enum):
    school = "school"
    university = "university"
    company = "company"


class Region(str, enum.Enum):
    eu = "eu"
    us = "us"


class Role(str, enum.Enum):
    admin = "admin"
    teacher = "teacher"
    student = "student"
    parent = "parent"
