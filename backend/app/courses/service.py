import uuid
from pathlib import PurePosixPath

from fastapi import UploadFile
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core import storage
from app.core.config import settings
from app.core.errors import (
    BadRequestError,
    NotFoundError,
    PayloadTooLargeError,
    ServiceUnavailableError,
)
from app.courses.schemas import CourseCreate, CourseOut, FileOut
from app.models import Course, CourseFile, User

# extension -> (file_type stored in the database, content type sent to Storage)
ALLOWED_TYPES = {
    "pdf": ("pdf", "application/pdf"),
    "pptx": ("pptx", "application/vnd.openxmlformats-officedocument.presentationml.presentation"),
    "docx": ("docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
   # ,"mp4": ("video", "video/mp4"),
   # "mov": ("video", "video/quicktime"),
   #     "webm": ("video", "video/webm"),
}


def _to_out(course: Course, file_count: int) -> CourseOut:
    return CourseOut(
        course_id=course.course_id, title=course.title, subject=course.subject,
        status=course.status, version=course.version, file_count=file_count,
        created_at=course.created_at,
    )


def _file_counts(session: Session, course_ids: list[uuid.UUID]) -> dict[uuid.UUID, int]:
    if not course_ids:
        return {}
    rows = session.execute(
        select(CourseFile.course_id, func.count())
        .where(CourseFile.course_id.in_(course_ids))
        .group_by(CourseFile.course_id)
    )
    return {course_id: count for course_id, count in rows}


def get_owned_course(session: Session, teacher: User, course_id: uuid.UUID) -> Course:
    """404 (not 403) for other teachers' courses, so ids can't be probed."""
    course = session.get(Course, course_id)
    if course is None or course.teacher_id != teacher.user_id:
        raise NotFoundError("Course not found")
    return course


def create_course(session: Session, teacher: User, data: CourseCreate) -> CourseOut:
    course = Course(
        org_id=teacher.org_id, teacher_id=teacher.user_id,
        title=data.title.strip(), subject=(data.subject or "").strip() or None,
    )
    session.add(course)
    session.commit()
    return _to_out(course, 0)


def list_courses(session: Session, teacher: User) -> list[CourseOut]:
    courses = session.scalars(
        select(Course).where(Course.teacher_id == teacher.user_id).order_by(Course.created_at.desc())
    ).all()
    counts = _file_counts(session, [c.course_id for c in courses])
    return [_to_out(c, counts.get(c.course_id, 0)) for c in courses]


def get_course(session: Session, teacher: User, course_id: uuid.UUID) -> CourseOut:
    course = get_owned_course(session, teacher, course_id)
    return _to_out(course, _file_counts(session, [course.course_id]).get(course.course_id, 0))


def list_files(session: Session, teacher: User, course_id: uuid.UUID) -> list[CourseFile]:
    course = get_owned_course(session, teacher, course_id)
    return list(
        session.scalars(
            select(CourseFile).where(CourseFile.course_id == course.course_id).order_by(CourseFile.uploaded_at.desc())
        )
    )


def upload_file(session: Session, teacher: User, course_id: uuid.UUID, upload: UploadFile) -> FileOut:
    course = get_owned_course(session, teacher, course_id)

    original_name = PurePosixPath((upload.filename or "").replace("\\", "/")).name
    extension = original_name.rsplit(".", 1)[-1].lower() if "." in original_name else ""
    if extension not in ALLOWED_TYPES:
        allowed = ", ".join(sorted(ALLOWED_TYPES))
        raise BadRequestError(f"Unsupported file type. Allowed: {allowed}")
    file_type, content_type = ALLOWED_TYPES[extension]

    limit = settings.max_upload_mb * 1024 * 1024
    data = upload.file.read(limit + 1)  # read one byte past the limit to detect oversize files
    if len(data) > limit:
        raise PayloadTooLargeError(f"File is larger than {settings.max_upload_mb} MB")
    if not data:
        raise BadRequestError("The file is empty")

    # Storage key uses ids only, so odd characters in the original name can never break it.
    file_id = uuid.uuid4()
    path = f"{course.course_id}/{file_id}.{extension}"
    try:
        storage.upload(path, data, content_type)
    except Exception as exc:
        raise ServiceUnavailableError("Could not store the file, please try again") from exc

    record = CourseFile(
        file_id=file_id, course_id=course.course_id, file_name=original_name[:255],
        file_type=file_type, file_url=path,
    )
    session.add(record)
    try:
        session.commit()
    except Exception:
        session.rollback()
        _remove_quietly(path)  # don't leave an orphan object behind
        raise
    return FileOut.model_validate(record)


def delete_file(session: Session, teacher: User, course_id: uuid.UUID, file_id: uuid.UUID) -> None:
    course = get_owned_course(session, teacher, course_id)
    record = session.get(CourseFile, file_id)
    if record is None or record.course_id != course.course_id:
        raise NotFoundError("File not found")
    path = record.file_url
    session.delete(record)  # chunks go with it (cascade)
    session.commit()
    if path:
        _remove_quietly(path)


def _remove_quietly(path: str) -> None:
    try:
        storage.remove(path)
    except Exception:
        pass  # the database is the source of truth; a leftover object is harmless
