from pydantic import BaseModel
from typing import Optional


class CardCreate(BaseModel):
    name: str
    strength: int
    faction: str
    type: str
    description: Optional[str] = None


class CardResponse(BaseModel):
    id: int
    name: str
    strength: int
    faction: str
    type: str
    description: Optional[str] = None
