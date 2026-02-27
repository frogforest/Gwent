import os
from typing import List, Optional

import httpx

CARD_SERVICE_URL = os.getenv("CARD_SERVICE_URL", "http://localhost:8002")
DECK_SERVICE_URL = os.getenv("DECK_SERVICE_URL", "http://localhost:8001")


def get_card_strength(card_id: int) -> Optional[int]:
    try:
        resp = httpx.get(f"{CARD_SERVICE_URL}/cards/{card_id}", timeout=3.0)
        if resp.status_code == 200:
            return resp.json().get("strength")
        return None
    except httpx.RequestError:
        return None


def get_deck_card_ids(deck_id: int, token: str) -> List[int]:
    try:
        resp = httpx.get(
            f"{DECK_SERVICE_URL}/decks/{deck_id}",
            headers={"Authorization": f"Bearer {token}"},
            timeout=3.0,
        )
        if resp.status_code == 200:
            return resp.json().get("card_ids", [])
        return []
    except httpx.RequestError:
        return []
