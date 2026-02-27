from typing import Optional


def apply_move(
    game: dict,
    player_id: int,
    card_id: int,
    card_strength: int,
) -> Optional[str]:
    """
    Apply a player move to the game dict in-place.
    Returns an error string if the move is invalid, else None.
    """
    if game["state"] != "in_progress":
        return "Game is already finished"

    if game["current_turn"] != player_id:
        return "It is not your turn"

    if player_id == game["player1_id"]:
        hand_key = "player1_hand"
        score_key = "score1"
        other_player_id = game["player2_id"]
        other_hand_key = "player2_hand"
    elif player_id == game["player2_id"]:
        hand_key = "player2_hand"
        score_key = "score2"
        other_player_id = game["player1_id"]
        other_hand_key = "player1_hand"
    else:
        return "Player is not part of this game"

    if card_id not in game[hand_key]:
        return "Card is not in your hand"

    game[hand_key].remove(card_id)
    game[score_key] += card_strength

    if game[other_hand_key]:
        game["current_turn"] = other_player_id
    elif not game[hand_key]:
        _finish_game(game)
    else:
        pass

    return None


def _finish_game(game: dict) -> None:
    game["state"] = "finished"
    s1 = game["score1"]
    s2 = game["score2"]
    if s1 > s2:
        game["winner"] = game["player1_id"]
    elif s2 > s1:
        game["winner"] = game["player2_id"]
    else:
        game["winner"] = None
