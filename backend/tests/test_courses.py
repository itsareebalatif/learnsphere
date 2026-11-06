import uuid

import pytest

from app.core import storage
from app.core.config import settings
from app.models.enums import Role

PDF = ("notes.pdf", b"%PDF-1.4 hello", "application/pdf")


def _upload(client, course_id, file=PDF):
    name, content, mime = file
    return client.post(f"/api/courses/{course_id}/files", files={"file": (name, content, mime)})


@pytest.fixture()
def teacher_client(client_as, make_user):
    return client_as(make_user("t@x.com", Role.teacher))


def test_student_cannot_create_course(client_as, make_user):
    assert client_as(make_user("s@x.com", Role.student)).post("/api/courses", json={"title": "x"}).status_code == 403


def test_create_and_list_courses(teacher_client):
    made = teacher_client.post("/api/courses", json={"title": "Biology", "subject": "Science"})
    assert made.status_code == 200
    assert made.json()["status"] == "draft" and made.json()["file_count"] == 0
    assert [c["title"] for c in teacher_client.get("/api/courses").json()] == ["Biology"]


def test_upload_stores_file_and_lists_it(teacher_client, fake_storage):
    course_id = teacher_client.post("/api/courses", json={"title": "Bio"}).json()["course_id"]

    res = _upload(teacher_client, course_id)
    assert res.status_code == 200
    body = res.json()
    assert (body["file_name"], body["file_type"], body["status"]) == ("notes.pdf", "pdf", "uploaded")

    assert len(fake_storage) == 1
    (path, data), = fake_storage.items()
    assert path.startswith(f"{course_id}/") and path.endswith(".pdf") and data == PDF[1]

    assert [f["file_name"] for f in teacher_client.get(f"/api/courses/{course_id}/files").json()] == ["notes.pdf"]
    assert teacher_client.get(f"/api/courses/{course_id}").json()["file_count"] == 1


def test_video_is_not_supported_yet(teacher_client, fake_storage):
    """Video needs the Whisper transcription step (later); the types are disabled in ALLOWED_TYPES."""
    course_id = teacher_client.post("/api/courses", json={"title": "Bio"}).json()["course_id"]
    assert _upload(teacher_client, course_id, ("lecture.mp4", b"data", "video/mp4")).status_code == 400
    assert fake_storage == {}


def test_rejects_bad_type_empty_and_oversize(teacher_client, fake_storage, monkeypatch):
    course_id = teacher_client.post("/api/courses", json={"title": "Bio"}).json()["course_id"]
    assert _upload(teacher_client, course_id, ("virus.exe", b"x", "application/octet-stream")).status_code == 400
    assert _upload(teacher_client, course_id, ("noext", b"x", "text/plain")).status_code == 400
    assert _upload(teacher_client, course_id, ("empty.pdf", b"", "application/pdf")).status_code == 400
    monkeypatch.setattr(settings, "max_upload_mb", 0)
    assert _upload(teacher_client, course_id).status_code == 413
    assert fake_storage == {}


def test_storage_failure_returns_503_and_saves_no_row(teacher_client, monkeypatch):
    def boom(*args):
        raise RuntimeError("storage down")

    monkeypatch.setattr(storage, "upload", boom)
    course_id = teacher_client.post("/api/courses", json={"title": "Bio"}).json()["course_id"]
    assert _upload(teacher_client, course_id).status_code == 503
    assert teacher_client.get(f"/api/courses/{course_id}/files").json() == []


def test_delete_file_removes_row_and_object(teacher_client, fake_storage):
    course_id = teacher_client.post("/api/courses", json={"title": "Bio"}).json()["course_id"]
    file_id = _upload(teacher_client, course_id).json()["file_id"]
    assert teacher_client.delete(f"/api/courses/{course_id}/files/{file_id}").status_code == 204
    assert fake_storage == {}
    assert teacher_client.get(f"/api/courses/{course_id}/files").json() == []
    assert teacher_client.delete(f"/api/courses/{course_id}/files/{file_id}").status_code == 404


def test_other_teacher_cannot_see_or_upload(client_as, make_user, fake_storage):
    owner = client_as(make_user("a@x.com", Role.teacher))
    course_id = owner.post("/api/courses", json={"title": "Bio"}).json()["course_id"]
    file_id = _upload(owner, course_id).json()["file_id"]

    other = client_as(make_user("b@x.com", Role.teacher))
    assert other.get("/api/courses").json() == []
    assert other.get(f"/api/courses/{course_id}").status_code == 404
    assert other.get(f"/api/courses/{course_id}/files").status_code == 404
    assert _upload(other, course_id).status_code == 404
    assert other.delete(f"/api/courses/{course_id}/files/{file_id}").status_code == 404
    assert other.get(f"/api/courses/{uuid.uuid4()}").status_code == 404
    assert len(fake_storage) == 1
