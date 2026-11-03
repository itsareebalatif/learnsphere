import os

# Settings are required at import time; give CI harmless defaults (never used for real calls).
for key, value in {
    "SUPABASE_URL": "http://localhost",
    "SUPABASE_ANON_KEY": "test",
    "SUPABASE_SERVICE_KEY": "test",
    "DATABASE_URL": "sqlite://",
}.items():
    os.environ.setdefault(key, value)

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.db import get_session
from app.core.security import get_current_user
from app.main import app
from app.models import Base, User
from app.models.enums import Role


@pytest.fixture()
def db():
    engine = create_engine("sqlite://", poolclass=StaticPool, connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    with sessionmaker(bind=engine, expire_on_commit=False)() as session:
        yield session


@pytest.fixture()
def make_user(db: Session):
    def _make(email: str, role: Role, org_id=None, name: str = "Test User") -> User:
        user = User(email=email, full_name=name, role=role, org_id=org_id)
        db.add(user)
        db.commit()
        return user

    return _make


@pytest.fixture()
def client_as(db: Session):
    """client_as(user) -> a TestClient whose requests are logged in as that user."""

    def _client(user: User | None) -> TestClient:
        app.dependency_overrides[get_session] = lambda: db
        if user is not None:
            app.dependency_overrides[get_current_user] = lambda: user
        else:
            app.dependency_overrides.pop(get_current_user, None)
        return TestClient(app)

    yield _client
    app.dependency_overrides.clear()
