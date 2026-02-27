import pytest
from fastapi.testclient import TestClient

import app.storage as storage
from app.main import app


@pytest.fixture(autouse=True)
def reset_storage():
    storage.reset()
    yield
    storage.reset()


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


def _create_game(
    client: TestClient,
    player1_id: int = 1,
    player2_id: int = 2,
    player1_deck_id: int = 10,
    player2_deck_id: int = 20,
) -> dict:
    resp = client.post(
        "/games",
        json={
            "player1_id": player1_id,
            "player2_id": player2_id,
            "player1_deck_id": player1_deck_id,
            "player2_deck_id": player2_deck_id,
        },
    )
    return resp.json()


def test_create_game(client):
    response = client.post(
        "/games",
        json={
            "player1_id": 1,
            "player2_id": 2,
            "player1_deck_id": 10,
            "player2_deck_id": 20,
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["player1_id"] == 1
    assert data["player2_id"] == 2
    assert data["state"] == "in_progress"
    assert data["score1"] == 0
    assert data["score2"] == 0


def test_create_game_sets_current_turn(client):
    game = _create_game(client, player1_id=5, player2_id=6)
    assert game["current_turn"] == 5


def test_get_game(client):
    game = _create_game(client)
    gid = game["id"]
    response = client.get(f"/games/{gid}")
    assert response.status_code == 200
    assert response.json()["id"] == gid


def test_get_game_not_found(client):
    response = client.get("/games/9999")
    assert response.status_code == 404


def test_multiple_games(client):
    game1 = _create_game(client, 1, 2, 10, 20)
    game2 = _create_game(client, 3, 4, 30, 40)
    assert game1["id"] != game2["id"]
    r1 = client.get(f"/games/{game1['id']}")
    r2 = client.get(f"/games/{game2['id']}")
    assert r1.status_code == 200
    assert r2.status_code == 200
    assert r1.json()["player1_id"] == 1
    assert r2.json()["player1_id"] == 3
