import uuid

import pytest
from sqlalchemy import select

from app.auth.service import sync_user
from app.core.errors import BadRequestError, ForbiddenError
from app.models import User
from app.models.enums import Role


def _identity(email, confirmed=True, **extra):
    identity = {"id": str(uuid.uuid4()), "email": email, **extra}
    if confirmed:
        identity["email_confirmed_at"] = "2026-01-01T00:00:00Z"
    return identity


def test_first_login_creates_a_teacher(db):
    user = sync_user(db, _identity("New@X.com", user_metadata={"full_name": "Nia New"}))
    assert (user.email, user.full_name, user.role) == ("new@x.com", "Nia New", Role.teacher)


def test_second_login_returns_the_same_user(db):
    identity = _identity("a@x.com")
    assert sync_user(db, identity).user_id == sync_user(db, identity).user_id


def test_invited_student_is_linked_on_verified_login(db, make_user):
    invited = make_user("kid@x.com", Role.student)
    identity = _identity("kid@x.com")
    linked = sync_user(db, identity)
    assert linked.user_id == invited.user_id and str(linked.auth_id) == identity["id"]
    assert linked.role == Role.student  # linking never changes the role


def test_unverified_email_cannot_claim_an_invited_account(db, make_user):
    make_user("kid@x.com", Role.student)
    with pytest.raises(ForbiddenError):
        sync_user(db, _identity("kid@x.com", confirmed=False))


def test_user_metadata_cannot_fake_email_verification(db, make_user):
    """Supabase lets users write their own user_metadata at sign-up, so it must never be trusted."""
    make_user("kid@x.com", Role.student)
    fake = _identity("kid@x.com", confirmed=False, user_metadata={"email_confirmed_at": "2026-01-01"})
    with pytest.raises(ForbiddenError):
        sync_user(db, fake)
    assert db.scalar(select(User).where(User.email == "kid@x.com")).auth_id is None


def test_malformed_identity_is_a_bad_request(db):
    with pytest.raises(BadRequestError):
        sync_user(db, {"email": "a@x.com"})
    with pytest.raises(BadRequestError):
        sync_user(db, {"id": "not-a-uuid", "email": "a@x.com"})
