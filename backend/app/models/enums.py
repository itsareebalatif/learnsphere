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


class CourseStatus(str, enum.Enum):
    draft = "draft"
    published = "published"


class FileStatus(str, enum.Enum):
    uploaded = "uploaded"
    processing = "processing"
    ready = "ready"
    failed = "failed"
