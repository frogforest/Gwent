import base64
import hashlib
import hmac
import json
import time
from typing import Optional

SECRET_KEY = "supersecretkey"


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
