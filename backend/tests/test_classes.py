import uuid

from sqlalchemy import select

from app.models import User
from app.models.enums import Role


def test_student_cannot_create_class(client_as, make_user):
    student = make_user("s@x.com", Role.student)
    assert client_as(student).post("/api/classes", json={"name": "Math"}).status_code == 403


def test_teacher_creates_class_adds_student_and_student_sees_it(client_as, make_user, db):
    teacher = make_user("t@x.com", Role.teacher, name="Tina Teacher")
    c = client_as(teacher)

    created = c.post("/api/classes", json={"name": "Math 101", "term": "Fall"})
    assert created.status_code == 200
    class_id = created.json()["class_id"]

    added = c.post(f"/api/classes/{class_id}/students", json={"email": "Kid@X.com", "full_name": "Kim Kid"})
    assert added.status_code == 200
    assert added.json()["email"] == "kid@x.com"
    assert added.json()["joined"] is False

    assert c.get("/api/classes").json()[0]["student_count"] == 1
    assert [s["full_name"] for s in c.get(f"/api/classes/{class_id}/students").json()] == ["Kim Kid"]

    # the new student, once linked to a login, sees the class
    student = client_as(db.scalar(select(User).where(User.email == "kid@x.com")))
    mine = student.get("/api/classes").json()
    assert [(m["name"], m["teacher_name"]) for m in mine] == [("Math 101", "Tina Teacher")]
    assert student.post("/api/classes", json={"name": "x"}).status_code == 403


def test_duplicate_student_rejected(client_as, make_user):
    c = client_as(make_user("t@x.com", Role.teacher))
    class_id = c.post("/api/classes", json={"name": "A"}).json()["class_id"]
    body = {"email": "kid@x.com"}
    assert c.post(f"/api/classes/{class_id}/students", json=body).status_code == 200
    assert c.post(f"/api/classes/{class_id}/students", json=body).status_code == 409


def test_teacher_cannot_touch_another_teachers_class(client_as, make_user):
    owner = client_as(make_user("a@x.com", Role.teacher))
    class_id = owner.post("/api/classes", json={"name": "A"}).json()["class_id"]

    other = client_as(make_user("b@x.com", Role.teacher))
    assert other.get(f"/api/classes/{class_id}/students").status_code == 404
    assert other.post(f"/api/classes/{class_id}/students", json={"email": "k@x.com"}).status_code == 404
    assert other.get("/api/classes").json() == []
    assert other.get(f"/api/classes/{uuid.uuid4()}").status_code == 404


def test_cannot_add_non_student_or_other_school_student(client_as, make_user, db):
    from app.models import Organisation
    from app.models.enums import OrgType, Region

    org_a = Organisation(name="A", type=OrgType.school, region=Region.eu)
    org_b = Organisation(name="B", type=OrgType.school, region=Region.eu)
    db.add_all([org_a, org_b])
    db.commit()
    make_user("boss@x.com", Role.admin, org_a.org_id)
    make_user("kid@b.com", Role.student, org_b.org_id)

    c = client_as(make_user("t@a.com", Role.teacher, org_a.org_id))
    class_id = c.post("/api/classes", json={"name": "A"}).json()["class_id"]
    assert c.post(f"/api/classes/{class_id}/students", json={"email": "boss@x.com"}).status_code == 400
    assert c.post(f"/api/classes/{class_id}/students", json={"email": "kid@b.com"}).status_code == 409
