"""Checks that the backend can really write to the Supabase Storage bucket.

Run from the backend folder:  python scripts/check_storage.py
Uploads a tiny test file, lists it, then deletes it.
"""
import sys
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.core import storage  # noqa: E402
from app.core.config import settings  # noqa: E402

path = f"_smoke_test/{uuid.uuid4()}.pdf"
try:
    storage.upload(path, b"%PDF-1.4 smoke test", "application/pdf")
    print(f"OK  uploaded to bucket '{settings.storage_bucket}'")
    names = [o["name"] for o in storage._bucket().list("_smoke_test")]
    print("OK  listed:", names)
finally:
    try:
        storage.remove(path)
        print("OK  removed the test file")
    except Exception:
        pass
