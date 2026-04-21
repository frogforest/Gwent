import pytest
from fastapi.testclient import TestClient

import app.storage as storage
from app.main import app


@pytest.fixture
def client():
    with TestClient(app) as c:
        storage.reset()
        yield c
        storage.reset()


def _create_card(
    client: TestClient,
    name: str = "Test Card",
    strength: int = 5,
    faction: str = "Neutral",
    card_type: str = "Unit",
) -> dict:
    resp = client.post(
        "/cards",
        json={
            "name": name,
            "strength": strength,
            "faction": faction,
            "type": card_type,
        },
    )
    return resp.json()


def test_create_card(client):
    response = client.post(
        "/cards",
        json={
            "name": "Fireball",
            "strength": 8,
            "faction": "Nilfgaard",
            "type": "Spell",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Fireball"
    assert data["strength"] == 8


def test_get_card(client):
    card = _create_card(client, "Arrow", 3, "Northern Realms", "Unit")
    cid = card["id"]
    response = client.get(f"/cards/{cid}")
    assert response.status_code == 200
    assert response.json()["name"] == "Arrow"


def test_get_card_not_found(client):
    response = client.get("/cards/9999")
    assert response.status_code == 404


def test_list_cards(client):
    _create_card(client, "A", 5, "Neutral", "Unit")
    _create_card(client, "B", 3, "Monster", "Hero")
    response = client.get("/cards")
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_filter_by_faction(client):
    _create_card(client, "A", 5, "Neutral", "Unit")
    _create_card(client, "B", 3, "Monster", "Hero")
    response = client.get("/cards?faction=Neutral")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["faction"] == "Neutral"


def test_filter_by_type(client):
    _create_card(client, "A", 5, "Neutral", "Unit")
    _create_card(client, "B", 3, "Monster", "Hero")
    response = client.get("/cards?type=Hero")
    assert response.status_code == 200
    data = response.json()
    assert all(c["type"] == "Hero" for c in data)


def test_filter_by_min_strength(client):
    _create_card(client, "Weak", 2, "Neutral", "Unit")
    _create_card(client, "Strong", 10, "Neutral", "Hero")
    response = client.get("/cards?min_strength=5")
    assert response.status_code == 200
    data = response.json()
    assert all(c["strength"] >= 5 for c in data)
