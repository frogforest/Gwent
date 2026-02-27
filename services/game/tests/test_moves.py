from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

import app.storage as storage
from app.main import app
from app.storage import make_game

MOCK_STRENGTH = "app.routers.games.get_card_strength"


@pytest.fixture(autouse=True)
def reset_storage():
    storage.reset()
    yield
    storage.reset()


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


def _seed_game(
    player1_hand=None,
    player2_hand=None,
    player1_id=1,
    player2_id=2,
) -> dict:
    gid = storage.next_game_id()
    game = make_game(
        gid=gid,
        player1_id=player1_id,
        player2_id=player2_id,
        player1_deck_id=10,
        player2_deck_id=20,
        player1_hand=player1_hand or [101, 102],
        player2_hand=player2_hand or [201, 202],
    )
    storage.games[gid] = game
    return game


@patch(MOCK_STRENGTH, return_value=5)
def test_move_basic(mock_strength, client):
    game = _seed_game()
    gid = game["id"]

    resp = client.post(
        f"/games/{gid}/moves",
        json={"player_id": 1, "card_id": 101},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["score1"] == 5
    assert 101 not in data["player1_hand"]


@patch(MOCK_STRENGTH, return_value=7)
def test_move_switches_turn(mock_strength, client):
    game = _seed_game()
    gid = game["id"]

    resp = client.post(
        f"/games/{gid}/moves",
        json={"player_id": 1, "card_id": 101},
    )
    assert resp.json()["current_turn"] == 2


@patch(MOCK_STRENGTH, return_value=5)
def test_move_wrong_turn(mock_strength, client):
    game = _seed_game()
    gid = game["id"]

    resp = client.post(
        f"/games/{gid}/moves",
        json={"player_id": 2, "card_id": 201},
    )
    assert resp.status_code == 400
    assert "turn" in resp.json()["detail"].lower()


@patch(MOCK_STRENGTH, return_value=5)
def test_move_card_not_in_hand(mock_strength, client):
    game = _seed_game()
    gid = game["id"]

    resp = client.post(
        f"/games/{gid}/moves",
        json={"player_id": 1, "card_id": 999},
    )
    assert resp.status_code == 400


@patch(MOCK_STRENGTH, return_value=None)
def test_move_card_service_unavailable(mock_strength, client):
    game = _seed_game()
    gid = game["id"]

    resp = client.post(
        f"/games/{gid}/moves",
        json={"player_id": 1, "card_id": 101},
    )
    assert resp.status_code == 502


def test_move_game_not_found(client):
    resp = client.post(
        "/games/9999/moves",
        json={"player_id": 1, "card_id": 1},
    )
    assert resp.status_code == 404


@patch(MOCK_STRENGTH, return_value=10)
def test_winner_determined_when_hands_empty(mock_strength, client):
    game = _seed_game(player1_hand=[101], player2_hand=[201])
    gid = game["id"]

    client.post(f"/games/{gid}/moves", json={"player_id": 1, "card_id": 101})
    resp = client.post(f"/games/{gid}/moves", json={"player_id": 2, "card_id": 201})

    data = resp.json()
    assert data["state"] == "finished"
    assert data["winner"] is None


@patch(MOCK_STRENGTH)
def test_winner_player1_wins(mock_strength, client):
    mock_strength.side_effect = [15, 5]
    game = _seed_game(player1_hand=[101], player2_hand=[201])
    gid = game["id"]

    client.post(f"/games/{gid}/moves", json={"player_id": 1, "card_id": 101})
    resp = client.post(f"/games/{gid}/moves", json={"player_id": 2, "card_id": 201})

    data = resp.json()
    assert data["state"] == "finished"
    assert data["winner"] == 1
    assert data["score1"] == 15
    assert data["score2"] == 5


@patch(MOCK_STRENGTH)
def test_winner_player2_wins(mock_strength, client):
    mock_strength.side_effect = [3, 12]
    game = _seed_game(player1_hand=[101], player2_hand=[201])
    gid = game["id"]

    client.post(f"/games/{gid}/moves", json={"player_id": 1, "card_id": 101})
    resp = client.post(f"/games/{gid}/moves", json={"player_id": 2, "card_id": 201})

    data = resp.json()
    assert data["state"] == "finished"
    assert data["winner"] == 2


@patch(MOCK_STRENGTH, return_value=5)
def test_cannot_move_in_finished_game(mock_strength, client):
    game = _seed_game(player1_hand=[101], player2_hand=[201])
    gid = game["id"]

    client.post(f"/games/{gid}/moves", json={"player_id": 1, "card_id": 101})
    client.post(f"/games/{gid}/moves", json={"player_id": 2, "card_id": 201})

    resp = client.post(f"/games/{gid}/moves", json={"player_id": 1, "card_id": 999})
    assert resp.status_code == 400
    assert "finished" in resp.json()["detail"].lower()
