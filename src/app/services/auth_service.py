import hashlib
import hmac
import secrets
from datetime import UTC, datetime, timedelta

import jwt

from ..config import settings
from ..exceptions import AppError
from ..models.user import User


def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    h = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 100_000)
    return f"{salt}:{h.hex()}"


def verify_password(password: str, hashed: str) -> bool:
    salt, h = hashed.split(":", 1)
    expected = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 100_000)
    return hmac.compare_digest(expected, bytes.fromhex(h))


def create_token(user: User) -> str:
    payload = {
        "sub": str(user.id),
        "username": user.username,
        "exp": datetime.now(UTC) + timedelta(days=30),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm="HS256")


def decode_token(token: str) -> dict[str, str | int]:
    try:
        payload: dict[str, str | int] = jwt.decode(token, settings.jwt_secret, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError as err:
        raise AppError("Token expired", 401) from err
    except jwt.InvalidTokenError as err:
        raise AppError("Invalid token", 401) from err
