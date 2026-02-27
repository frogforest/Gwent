import hashlib
import hmac
import json
import time
import base64
from typing import Optional

SECRET_KEY = "supersecretkey"


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(password: str, hashed: str) -> bool:
    return hash_password(password) == hashed


def create_jwt(payload: dict, expires_in: int = 3600) -> str:
    header = (
        base64.urlsafe_b64encode(json.dumps({"alg": "HS256", "typ": "JWT"}).encode())
        .rstrip(b"=")
        .decode()
    )
    payload_copy = {**payload, "exp": int(time.time()) + expires_in}
    body = (
        base64.urlsafe_b64encode(json.dumps(payload_copy).encode())
        .rstrip(b"=")
        .decode()
    )
    signature = hmac.new(
        SECRET_KEY.encode(),
        f"{header}.{body}".encode(),
        hashlib.sha256,
    ).digest()
    sig = base64.urlsafe_b64encode(signature).rstrip(b"=").decode()
    return f"{header}.{body}.{sig}"


def decode_jwt(token: str) -> Optional[dict]:
    try:
        parts = token.split(".")
        if len(parts) != 3:
            return None
        header, body, sig = parts
        expected_sig = (
            base64.urlsafe_b64encode(
                hmac.new(
                    SECRET_KEY.encode(),
                    f"{header}.{body}".encode(),
                    hashlib.sha256,
                ).digest()
            )
            .rstrip(b"=")
            .decode()
        )
        if not hmac.compare_digest(sig, expected_sig):
            return None
        padding = 4 - len(body) % 4
        payload = json.loads(base64.urlsafe_b64decode(body + "=" * padding).decode())
        if payload.get("exp", 0) < time.time():
            return None
        return payload
    except Exception:
        return None
