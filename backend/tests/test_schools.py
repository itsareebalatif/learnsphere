from app.models.enums import Role


def test_only_admin_can_create_school(client_as, make_user):
    teacher = make_user("t@x.com", Role.teacher)
    assert client_as(teacher).post("/api/schools", json={"name": "Oak High"}).status_code == 403


def test_admin_creates_school_then_invites_users(client_as, make_user):
    admin = make_user("a@x.com", Role.admin)
    c = client_as(admin)

    assert c.get("/api/schools/me").status_code == 404
    assert c.post("/api/schools/me/users", json={"email": "t@x.com", "full_name": "T", "role": "teacher"}).status_code == 409

    made = c.post("/api/schools", json={"name": "Oak High", "type": "school", "region": "eu"})
    assert made.status_code == 200
    assert c.post("/api/schools", json={"name": "Again"}).status_code == 409
    assert c.get("/api/schools/me").json()["name"] == "Oak High"

    invited = c.post("/api/schools/me/users", json={"email": "T@x.com", "full_name": "Tess", "role": "teacher"})
    assert invited.status_code == 200 and invited.json()["joined"] is False
    assert c.post("/api/schools/me/users", json={"email": "t@x.com", "full_name": "Tess", "role": "teacher"}).status_code == 409
    assert c.post("/api/schools/me/users", json={"email": "z@x.com", "full_name": "Z", "role": "admin"}).status_code == 400

    users = c.get("/api/schools/me/users").json()
    assert {u["email"] for u in users} == {"a@x.com", "t@x.com"}
