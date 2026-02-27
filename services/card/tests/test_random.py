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


def _add_cards(client: TestClient, n: int = 10) -> None:
    factions = ["Neutral", "Monster", "Northern Realms"]
    for i in range(n):
        client.post(
            "/cards",
            json={
                "name": f"Card {i}",
                "strength": i + 1,
                "faction": factions[i % 3],
                "type": "Unit",
            },
        )


def test_random_returns_default_count(client):
    _add_cards(client, 10)
    resp = client.get("/cards/random")
    assert resp.status_code == 200
    assert len(resp.json()) == 5


def test_random_custom_count(client):
    _add_cards(client, 10)
    resp = client.get("/cards/random?count=3")
    assert resp.status_code == 200
    assert len(resp.json()) == 3


def test_random_count_capped_by_available(client):
    _add_cards(client, 4)
    resp = client.get("/cards/random?count=10")
    assert resp.status_code == 200
    assert len(resp.json()) == 4


def test_random_with_faction_filter(client):
    _add_cards(client, 9)
    resp = client.get("/cards/random?count=20&faction=Neutral")
    assert resp.status_code == 200
    for card in resp.json():
        assert card["faction"] == "Neutral"


def test_random_empty_catalog(client):
    resp = client.get("/cards/random")
    assert resp.status_code == 200
    assert resp.json() == []


def test_random_returns_valid_card_objects(client):
    _add_cards(client, 5)
    resp = client.get("/cards/random?count=5")
    assert resp.status_code == 200
    for card in resp.json():
        assert "id" in card
        assert "name" in card
        assert "strength" in card
        assert "faction" in card
        assert "type" in card
