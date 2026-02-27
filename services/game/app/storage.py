from typing import Dict, List, Optional

games: Dict[int, dict] = {}
_game_counter = 1


def next_game_id() -> int:
    global _game_counter
    gid = _game_counter
    _game_counter += 1
    return gid


def make_game(
    gid: int,
    player1_id: int,
    player2_id: int,
    player1_deck_id: int,
    player2_deck_id: int,
    player1_hand: Optional[List[int]] = None,
    player2_hand: Optional[List[int]] = None,
) -> dict:
    return {
        "id": gid,
        "player1_id": player1_id,
        "player2_id": player2_id,
        "player1_deck_id": player1_deck_id,
        "player2_deck_id": player2_deck_id,
        "state": "in_progress",
        "current_turn": player1_id,
        "score1": 0,
        "score2": 0,
        "player1_hand": list(player1_hand or []),
        "player2_hand": list(player2_hand or []),
        "winner": None,
    }


def reset() -> None:
    global _game_counter
    games.clear()
    _game_counter = 1
