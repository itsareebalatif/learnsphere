import uuid

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.classes.schemas import AddStudentIn, ClassCreate, ClassOut, StudentOut
from app.models import Enrolment, SchoolClass, User
from app.models.enums import Role


def _to_out(cls: SchoolClass, student_count: int) -> ClassOut:
    return ClassOut(
        class_id=cls.class_id, name=cls.name, term=cls.term,
        teacher_name=cls.teacher.full_name, student_count=student_count,
        created_at=cls.created_at,
    )


def _student_counts(session: Session, class_ids: list[uuid.UUID]) -> dict[uuid.UUID, int]:
    if not class_ids:
        return {}
    rows = session.execute(
        select(Enrolment.class_id, func.count())
        .where(Enrolment.class_id.in_(class_ids))
        .group_by(Enrolment.class_id)
    )
    return {class_id: count for class_id, count in rows}


def create_class(session: Session, teacher: User, data: ClassCreate) -> ClassOut:
    cls = SchoolClass(
        org_id=teacher.org_id, teacher_id=teacher.user_id,
        name=data.name.strip(), term=(data.term or "").strip() or None,
    )
    session.add(cls)
    session.commit()
    return _to_out(cls, 0)


def list_my_classes(session: Session, user: User) -> list[ClassOut]:
    query = select(SchoolClass).order_by(SchoolClass.created_at.desc())
    if user.role == Role.teacher:
        query = query.where(SchoolClass.teacher_id == user.user_id)
    else:  # student
        query = query.join(Enrolment, Enrolment.class_id == SchoolClass.class_id).where(
            Enrolment.student_id == user.user_id
        )
    classes = session.scalars(query).all()
    counts = _student_counts(session, [c.class_id for c in classes])
    return [_to_out(c, counts.get(c.class_id, 0)) for c in classes]


def get_owned_class(session: Session, teacher: User, class_id: uuid.UUID) -> SchoolClass:
    """404 (not 403) for other teachers' classes, so ids can't be probed."""
    cls = session.get(SchoolClass, class_id)
    if cls is None or cls.teacher_id != teacher.user_id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Class not found")
    return cls


def get_class_out(session: Session, teacher: User, class_id: uuid.UUID) -> ClassOut:
    cls = get_owned_class(session, teacher, class_id)
    return _to_out(cls, _student_counts(session, [cls.class_id]).get(cls.class_id, 0))


def list_students(session: Session, teacher: User, class_id: uuid.UUID) -> list[StudentOut]:
    cls = get_owned_class(session, teacher, class_id)
    students = session.scalars(
        select(User)
        .join(Enrolment, Enrolment.student_id == User.user_id)
        .where(Enrolment.class_id == cls.class_id)
        .order_by(User.full_name)
    ).all()
    return [_student_out(s) for s in students]


def add_student(session: Session, teacher: User, class_id: uuid.UUID, data: AddStudentIn) -> StudentOut:
    cls = get_owned_class(session, teacher, class_id)
    email = data.email.lower()
    student = session.scalar(select(User).where(User.email == email))

    if student is None:
        # New student: pre-create the row; it links to their login on first sign-in.
        student = User(
            email=email,
            full_name=(data.full_name or email.split("@")[0]).strip(),
            role=Role.student,
            org_id=teacher.org_id,
        )
        session.add(student)
        session.flush()
    elif student.role != Role.student:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "That email belongs to a non-student account")
    elif student.org_id != teacher.org_id:
        # Never reveal or pull in students from another school.
        raise HTTPException(status.HTTP_409_CONFLICT, "This email cannot be added to your class")

    already = session.scalar(
        select(Enrolment).where(
            Enrolment.class_id == cls.class_id, Enrolment.student_id == student.user_id
        )
    )
    if already is not None:
        raise HTTPException(status.HTTP_409_CONFLICT, "Student is already in this class")

    session.add(Enrolment(class_id=cls.class_id, student_id=student.user_id))
    session.commit()
    return _student_out(student)


def _student_out(student: User) -> StudentOut:
    return StudentOut(
        user_id=student.user_id, email=student.email,
        full_name=student.full_name, joined=student.auth_id is not None,
    )
