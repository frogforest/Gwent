import os

import httpx

CARD_SERVICE_URL = os.getenv("CARD_SERVICE_URL", "http://localhost:8002")


def card_exists(card_id: int) -> bool:
    try:
        resp = httpx.get(f"{CARD_SERVICE_URL}/cards/{card_id}", timeout=3.0)
        return resp.status_code == 200
    except httpx.RequestError:
        return False
