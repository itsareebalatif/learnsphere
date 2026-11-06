from fastapi.testclient import TestClient
from sqlalchemy.exc import IntegrityError

from app.core.errors import ConflictError
from app.main import app


def test_missing_token_is_401_with_standard_body():
    res = TestClient(app).get("/api/me")
    assert res.status_code == 401
    assert res.json() == {"detail": "Missing bearer token"}
    assert res.headers["www-authenticate"] == "Bearer"


def test_app_error_integrity_error_and_unexpected_error_are_handled():
    @app.get("/_boom/{kind}")
    def boom(kind: str):
        if kind == "conflict":
            raise ConflictError("already there")
        if kind == "integrity":
            raise IntegrityError("insert", {}, Exception("duplicate key"))
        raise RuntimeError("secret internal detail")

    client = TestClient(app, raise_server_exceptions=False)
    assert client.get("/_boom/conflict").json() == {"detail": "already there"}
    assert client.get("/_boom/integrity").status_code == 409

    res = client.get("/_boom/other")
    assert res.status_code == 500
    assert res.json() == {"detail": "Something went wrong on our side"}  # no internals leaked
