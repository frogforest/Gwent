from typing import List, Optional

from fastapi import APIRouter, HTTPException, Header

from app.auth import decode_jwt
from app.http_client import card_exists
from app.models import DeckCreate, DeckResponse
import app.storage as storage

router = APIRouter()


def get_current_user_id(authorization: Optional[str]) -> int:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid token")
    token = authorization[7:]
    payload = decode_jwt(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return payload["sub"]


def _require_deck(deck_id: int, user_id: int) -> dict:
    deck = storage.decks.get(deck_id)
    if not deck:
        raise HTTPException(status_code=404, detail="Deck not found")
    if deck["user_id"] != user_id:
        raise HTTPException(status_code=403, detail="Forbidden")
    return deck


def _deck_to_response(deck: dict) -> DeckResponse:
    return DeckResponse(
        id=deck["id"],
        user_id=deck["user_id"],
        name=deck["name"],
        card_ids=list(deck.get("card_ids", [])),
    )


@router.post("/decks", response_model=DeckResponse, status_code=201)
def create_deck(
    body: DeckCreate, authorization: Optional[str] = Header(None)
) -> DeckResponse:
    user_id = get_current_user_id(authorization)
    did = storage.next_deck_id()
    storage.decks[did] = {
        "id": did,
        "user_id": user_id,
        "name": body.name,
        "card_ids": [],
    }
    return _deck_to_response(storage.decks[did])


@router.get("/decks", response_model=List[DeckResponse])
def list_decks(authorization: Optional[str] = Header(None)) -> List[DeckResponse]:
    user_id = get_current_user_id(authorization)
    return [
        _deck_to_response(d) for d in storage.decks.values() if d["user_id"] == user_id
    ]


@router.get("/decks/{deck_id}", response_model=DeckResponse)
def get_deck(deck_id: int, authorization: Optional[str] = Header(None)) -> DeckResponse:
    user_id = get_current_user_id(authorization)
    deck = _require_deck(deck_id, user_id)
    return _deck_to_response(deck)


@router.delete("/decks/{deck_id}", status_code=204)
def delete_deck(deck_id: int, authorization: Optional[str] = Header(None)) -> None:
    user_id = get_current_user_id(authorization)
    _require_deck(deck_id, user_id)
    del storage.decks[deck_id]


@router.post("/decks/{deck_id}/cards/{card_id}", response_model=DeckResponse)
def add_card_to_deck(
    deck_id: int,
    card_id: int,
    authorization: Optional[str] = Header(None),
) -> DeckResponse:
    user_id = get_current_user_id(authorization)
    deck = _require_deck(deck_id, user_id)

    if not card_exists(card_id):
        raise HTTPException(status_code=404, detail="Card not found in catalog")

    if card_id in deck["card_ids"]:
        raise HTTPException(status_code=409, detail="Card already in deck")

    deck["card_ids"].append(card_id)
    return _deck_to_response(deck)


@router.delete("/decks/{deck_id}/cards/{card_id}", response_model=DeckResponse)
def remove_card_from_deck(
    deck_id: int,
    card_id: int,
    authorization: Optional[str] = Header(None),
) -> DeckResponse:
    user_id = get_current_user_id(authorization)
    deck = _require_deck(deck_id, user_id)

    if card_id not in deck["card_ids"]:
        raise HTTPException(status_code=404, detail="Card not in deck")

    deck["card_ids"].remove(card_id)
    return _deck_to_response(deck)
