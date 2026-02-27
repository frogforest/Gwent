from typing import Dict, List

users: Dict[int, dict] = {}
decks: Dict[int, dict] = {}
_user_counter = 1
_deck_counter = 1


def next_user_id() -> int:
    global _user_counter
    uid = _user_counter
    _user_counter += 1
    return uid


def next_deck_id() -> int:
    global _deck_counter
    did = _deck_counter
    _deck_counter += 1
    return did


def get_deck_cards(deck_id: int) -> List[int]:
    deck = decks.get(deck_id)
    if deck is None:
        return []
    return list(deck.get("card_ids", []))


def reset() -> None:
    global _user_counter, _deck_counter
    users.clear()
    decks.clear()
    _user_counter = 1
    _deck_counter = 1
