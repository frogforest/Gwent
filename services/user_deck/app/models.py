from typing import List

from pydantic import BaseModel


class UserCreate(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    id: int
    username: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str


class DeckCreate(BaseModel):
    name: str


class DeckResponse(BaseModel):
    id: int
    user_id: int
    name: str
    card_ids: List[int] = []
