from fastapi import APIRouter, HTTPException, Header
from typing import Optional

from app.game_logic import apply_move
from app.http_client import get_card_strength, get_deck_card_ids
from app.models import GameCreate, GameResponse, MoveRequest
from app.storage import games, make_game, next_game_id

router = APIRouter()


def _to_response(game: dict) -> GameResponse:
    return GameResponse(**game)


@router.post("/games", response_model=GameResponse, status_code=201)
def create_game(
    body: GameCreate,
    authorization: Optional[str] = Header(None),
) -> GameResponse:
    token = ""
    if authorization and authorization.startswith("Bearer "):
        token = authorization[7:]

    p1_cards = get_deck_card_ids(body.player1_deck_id, token)
    p2_cards = get_deck_card_ids(body.player2_deck_id, token)

    gid = next_game_id()
    game = make_game(
        gid=gid,
        player1_id=body.player1_id,
        player2_id=body.player2_id,
        player1_deck_id=body.player1_deck_id,
        player2_deck_id=body.player2_deck_id,
        player1_hand=p1_cards,
        player2_hand=p2_cards,
    )
    games[gid] = game
    return _to_response(game)


@router.get("/games/{game_id}", response_model=GameResponse)
def get_game(game_id: int) -> GameResponse:
    game = games.get(game_id)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    return _to_response(game)


@router.post("/games/{game_id}/moves", response_model=GameResponse)
def make_move(game_id: int, body: MoveRequest) -> GameResponse:
    game = games.get(game_id)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")

    strength = get_card_strength(body.card_id)
    if strength is None:
        raise HTTPException(
            status_code=502,
            detail="Card service unavailable or card not found",
        )

    error = apply_move(game, body.player_id, body.card_id, strength)
    if error:
        raise HTTPException(status_code=400, detail=error)

    return _to_response(game)
