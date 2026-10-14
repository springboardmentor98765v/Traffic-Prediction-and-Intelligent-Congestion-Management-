"""Helpers shared by the M1 tests (own module name so it can't clash with other conftests)."""

import uuid

PASSWORD = "QaM1#Pass2026"


def new_email(prefix="qa.m1"):
    # Registration only accepts allow-listed domains (app/schemas/user.py).
    return f"{prefix}.{uuid.uuid4().hex[:8]}@gmail.com"


def bearer(token):
    return {"Authorization": f"Bearer {token}"}
