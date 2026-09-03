from datetime import datetime, timedelta, timezone

import pytest
from jose import jwt

from app.core.auth import create_access_token, decode_access_token
from app.core.config import settings


def test_round_trip_token():
    token = create_access_token(subject="demo")
    assert decode_access_token(token) == "demo"


def test_invalid_token_raises():
    with pytest.raises(ValueError):
        decode_access_token("not-a-real-token")


def test_expired_token_raises():
    expired_payload = {
        "sub": "demo",
        "exp": datetime.now(timezone.utc) - timedelta(minutes=1),
    }
    expired_token = jwt.encode(
        expired_payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm
    )
    with pytest.raises(ValueError):
        decode_access_token(expired_token)
