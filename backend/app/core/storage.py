"""Thin wrapper around Supabase Storage so the rest of the app never touches the SDK."""
from functools import lru_cache

from supabase import Client, create_client

from app.core.config import settings


@lru_cache
def _client() -> Client:
    # Service key: the backend decides who may upload; the bucket itself stays private.
    return create_client(settings.supabase_url, settings.supabase_service_key)


def _bucket():
    return _client().storage.from_(settings.storage_bucket)


def upload(path: str, data: bytes, content_type: str) -> None:
    _bucket().upload(path, data, {"content-type": content_type, "upsert": "false"})


def remove(path: str) -> None:
    _bucket().remove([path])
