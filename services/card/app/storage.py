from typing import Dict

cards: Dict[int, dict] = {}
_card_counter = 1


def next_card_id() -> int:
    global _card_counter
    cid = _card_counter
    _card_counter += 1
    return cid


def reset() -> None:
    global _card_counter
    cards.clear()
    _card_counter = 1
