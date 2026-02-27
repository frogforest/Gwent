from typing import List, Optional

from pydantic import BaseModel


class GameCreate(BaseModel):
    player1_id: int
    player2_id: int
    player1_deck_id: int
    player2_deck_id: int


class MoveRequest(BaseModel):
    player_id: int
    card_id: int


class GameResponse(BaseModel):
    id: int
    player1_id: int
    player2_id: int
    player1_deck_id: int
    player2_deck_id: int
    state: str
    current_turn: int
    score1: int
    score2: int
    player1_hand: List[int] = []
    player2_hand: List[int] = []
    winner: Optional[int] = None
