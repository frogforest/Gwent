import random as _random
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query

from app.models import CardCreate, CardResponse
import app.storage as storage

router = APIRouter()


@router.post("/cards", response_model=CardResponse, status_code=201)
def create_card(body: CardCreate) -> CardResponse:
    cid = storage.next_card_id()
    card = {
        "id": cid,
        "name": body.name,
        "strength": body.strength,
        "faction": body.faction,
        "type": body.type,
        "description": body.description,
    }
    storage.cards[cid] = card
    return CardResponse(**card)


@router.get("/cards/random", response_model=List[CardResponse])
def random_cards(
    count: int = Query(default=5, ge=1, le=50),
    faction: Optional[str] = None,
    type: Optional[str] = None,
) -> List[CardResponse]:
    result = list(storage.cards.values())
    if faction:
        result = [c for c in result if c["faction"] == faction]
    if type:
        result = [c for c in result if c["type"] == type]
    sample = _random.sample(result, min(count, len(result)))
    return [CardResponse(**c) for c in sample]


@router.get("/cards", response_model=List[CardResponse])
def list_cards(
    faction: Optional[str] = None,
    type: Optional[str] = None,
    min_strength: Optional[int] = None,
) -> List[CardResponse]:
    result = list(storage.cards.values())
    if faction:
        result = [c for c in result if c["faction"] == faction]
    if type:
        result = [c for c in result if c["type"] == type]
    if min_strength is not None:
        result = [c for c in result if c["strength"] >= min_strength]
    return [CardResponse(**c) for c in result]


@router.get("/cards/{card_id}", response_model=CardResponse)
def get_card(card_id: int) -> CardResponse:
    card = storage.cards.get(card_id)
    if not card:
        raise HTTPException(status_code=404, detail="Card not found")
    return CardResponse(**card)
